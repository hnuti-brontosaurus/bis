"""The ground each area covers, drawn on the managers' maps.

An area's outline wraps its boxes, bridging gaps between them, and where two
areas' boxes mingle (sectors of one forest) the ground goes to the nearer box:
the outlines are clipped to the Voronoi cells of every box, so they never
overlap. That needs all boxes at once, hence one pass over every area.
"""

import json
from uuid import uuid4

from django.core.cache import cache
from django.db import connection, transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from nest_boxes.models import Area, NestBox

# Metres, in ETRS89-LAEA, which covers the boxes abroad too
REACH = 80
# Boxes up to 2 * (REACH + GAP) apart share one patch of ground
GAP = 100
SIMPLIFY = 3
METRIC_SRID = 3035

GENERATION_KEY = "nest_boxes_outlines_generation"
TIMEOUT = 24 * 60 * 60

SQL = f"""
WITH points AS (
    SELECT area_id, ST_Transform(location, {METRIC_SRID}) AS geom
    FROM nest_boxes_nestbox
    WHERE status <> %(ended)s
),
-- Back in degrees, so that matching a cell to its box uses the location index
cells AS (
    SELECT ST_Transform((ST_Dump(ST_VoronoiPolygons(ST_Collect(geom)))).geom, 4326)
        AS cell
    FROM points
),
territories AS (
    SELECT box.area_id,
        ST_UnaryUnion(ST_Collect(ST_Transform(cells.cell, {METRIC_SRID}))) AS geom
    FROM cells
    JOIN nest_boxes_nestbox AS box
        ON box.status <> %(ended)s AND ST_Intersects(cells.cell, box.location)
    GROUP BY box.area_id
),
patches AS (
    SELECT area_id,
        ST_Buffer(
            ST_Buffer(ST_Collect(geom), %(reach)s + %(gap)s, 'quad_segs=4'),
            -%(gap)s,
            'quad_segs=4'
        ) AS geom
    FROM points
    GROUP BY area_id
)
SELECT area.id, area.name, ST_AsGeoJSON(
    ST_Transform(
        ST_SimplifyPreserveTopology(ST_Intersection(patches.geom, territories.geom),
                                    %(simplify)s),
        4326
    ),
    6
)
FROM patches
JOIN territories USING (area_id)
JOIN nest_boxes_area AS area ON area.id = patches.area_id
"""


def _compute():
    with connection.cursor() as cursor:
        cursor.execute(
            SQL,
            {
                "ended": NestBox.Status.ENDED,
                "reach": REACH,
                "gap": GAP,
                "simplify": SIMPLIFY,
            },
        )
        return [
            {"id": area_id, "name": name, "outline": json.loads(outline)}
            for area_id, name, outline in cursor.fetchall()
        ]


def area_outlines():
    """[{id, name, outline: GeoJSON}] of every area with a box that isn't ended."""
    generation = cache.get_or_set(GENERATION_KEY, lambda: uuid4().hex, None)
    return cache.get_or_set(f"nest_boxes_outlines:{generation}", _compute, TIMEOUT)


def invalidate():
    cache.delete(GENERATION_KEY)


@receiver(post_save, sender=NestBox)
@receiver(post_save, sender=Area)
@receiver(post_delete, sender=NestBox)
@receiver(post_delete, sender=Area)
def _invalidate_on_change(**kwargs):
    transaction.on_commit(invalidate)
