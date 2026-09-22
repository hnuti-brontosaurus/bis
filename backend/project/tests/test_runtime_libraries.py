"""Guards the runtime stage of backend/Dockerfile.

The image is built multi-stage: the compiler toolchain lives in the builder
and only a hand-picked set of shared libraries is installed alongside the
venv. Nothing else in the suite would notice a missing .so, because these
libraries are loaded by path or by ctypes rather than imported, so dropping
one would only surface in production.
"""

import pyheif
import pytest
from django.contrib.gis.gdal import SpatialReference
from django.contrib.gis.geos import Point
from weasyprint import HTML


def test_weasyprint_renders_text_with_an_embedded_font():
    empty = HTML(string="<p></p>").write_pdf()
    text = HTML(string="<p>Příliš žluťoučký kůň úpěl ďábelské ódy</p>").write_pdf()

    assert text.startswith(b"%PDF-")
    # With no font installed fontconfig finds nothing, weasyprint drops the
    # glyphs and the two PDFs come out near-identical in size.
    assert len(text) - len(empty) > 1000


def test_pyheif_native_extension_loads():
    # The wheel bundles its own libheif/libde265/libaom under pyheif.libs, so
    # reaching this error means that whole dlopen chain resolved.
    with pytest.raises(ValueError, match="not a HEIF/AVIF file"):
        pyheif.read(b"definitely not heif")


def test_geos_is_usable():
    assert Point(0, 0).distance(Point(3, 4)) == pytest.approx(5.0)


def test_gdal_is_usable():
    assert SpatialReference(4326).srid == 4326
