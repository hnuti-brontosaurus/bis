from event.models import *
from nested_admin.nested import NestedModelAdmin
from opportunities.models import Opportunity
from rangefilter.filters import DateRangeFilter

from bis.admin_permissions import PermissionMixin


@admin.register(Opportunity)
class OpportunityAdmin(PermissionMixin, NestedModelAdmin):
    list_display = (
        "name",
        "category",
        "contact_person",
        "start",
        "end",
        "on_web_start",
        "on_web_end",
        "location",
    )
    autocomplete_fields = "location", "contact_person"

    list_select_related = "category", "contact_person"
    list_filter = (
        "category",
        ("start", DateRangeFilter),
        ("end", DateRangeFilter),
        ("on_web_start", DateRangeFilter),
        ("on_web_end", DateRangeFilter),
    )

    search_fields = Opportunity.get_search_fields()
    exclude = ("_search_field",)
