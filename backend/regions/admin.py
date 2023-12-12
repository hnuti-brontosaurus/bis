from bis.admin_permissions import PermissionMixin
from django.contrib.gis.admin import OSMGeoAdmin
from event.models import *
from nested_admin.nested import NestedModelAdmin
from regions.models import Region, ZipCode


@admin.register(Region)
class RegionAdmin(PermissionMixin, OSMGeoAdmin):
    pass


@admin.register(ZipCode)
class ZipCodeAdmin(PermissionMixin, NestedModelAdmin):
    list_filter = ("region",)
    list_display = "zip_code", "region"
    list_select_related = ("region",)
    search_fields = ("zip_code",)
