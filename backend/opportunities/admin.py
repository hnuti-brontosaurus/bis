from nested_admin.nested import NestedModelAdmin
from rangefilter.filters import DateRangeFilter

from bis.admin_permissions import PermissionMixin
from event.models import *
from opportunities.models import Opportunity


@admin.register(Opportunity)
class OpportunityAdmin(PermissionMixin, NestedModelAdmin):
    list_display = 'name', 'category', 'contact_person', 'start', 'end', 'on_web_start', 'on_web_end', 'location'
    autocomplete_fields = 'location', 'contact_person'

    list_select_related = 'category', 'contact_person'
    list_filter = (
        'category',
        ('start', DateRangeFilter), ('end', DateRangeFilter),
        ('on_web_start', DateRangeFilter), ('on_web_end', DateRangeFilter),
    )

    search_fields = 'name', 'introduction'
