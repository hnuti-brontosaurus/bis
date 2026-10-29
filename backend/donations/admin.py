from bis.admin_filters import HasDonorFilter
from bis.admin_helpers import ListAwareRangeNumericFilter
from bis.admin_permissions import PermissionMixin
from bis.models import User
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.contrib.messages import ERROR, INFO
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.html import format_html
from donations.helpers import upload_bank_records
from donations.models import (
    Donation,
    Donor,
    FundraisingCampaign,
    UploadBankRecords,
)
from more_admin_filters import MultiSelectRelatedDropdownFilter
from nested_admin.nested import NestedModelAdmin
from rangefilter.filters import DateRangeFilter
from solo.admin import SingletonModelAdmin
from xlsx_export.export import export_to_xlsx


@admin.register(FundraisingCampaign)
class FundraisingCampaignAdmin(PermissionMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "telesales_link")
    readonly_fields = ("slug",)

    def get_fields(self, request, obj=None):
        if obj is None:
            return ("name",)
        return ("name", "slug")

    @admin.display(description="Telesales")
    def telesales_link(self, obj):
        url = reverse("admin:donations_telesales_worklist", args=[obj.id])
        return format_html('<a href="{}">Volat</a>', url)

    def get_urls(self):
        from django.urls import path
        from donations.views.telesales import (
            telesales_call_view,
            telesales_worklist_view,
        )

        def worklist_campaign(request, campaign_id):
            return telesales_worklist_view(self, request, campaign_id)

        def call(request, campaign_id, user_id):
            return telesales_call_view(self, request, campaign_id, user_id)

        custom = [
            path(
                "telesales/<int:campaign_id>/",
                self.admin_site.admin_view(worklist_campaign),
                name="donations_telesales_worklist",
            ),
            path(
                "telesales/<int:campaign_id>/call/<uuid:user_id>/",
                self.admin_site.admin_view(call),
                name="donations_telesales_call",
            ),
        ]
        return custom + super().get_urls()


@admin.register(Donation)
class DonationAdmin(PermissionMixin, NestedModelAdmin):
    actions = [export_to_xlsx]
    autocomplete_fields = ("donor",)
    list_display = "__str__", "donor", "donated_at", "donation_source", "info"
    list_filter = (
        ("amount", ListAwareRangeNumericFilter),
        ("donated_at", DateRangeFilter),
        HasDonorFilter,
        ("donation_source", MultiSelectRelatedDropdownFilter),
    )
    exclude = ("_import_id",)

    list_select_related = "donor__user", "donation_source"
    search_fields = User.get_search_fields(prefix="donor__user__")


@admin.register(Donor)
class DonorAdmin(PermissionMixin, admin.ModelAdmin):
    """Donors are edited on their user. This stays registered for
    DonationAdmin's donor autocomplete, and sends old links to the user."""

    search_fields = User.get_search_fields(prefix="user__")

    def has_module_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect(
            reverse("admin:bis_user_changelist") + "?columns=donor&is_donor=yes"
        )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        donor = get_object_or_404(self.get_queryset(request), pk=unquote(object_id))
        return HttpResponseRedirect(
            reverse("admin:bis_user_change", args=[donor.user_id])
        )


@admin.register(UploadBankRecords)
class UploadBankRecordsAdmin(PermissionMixin, SingletonModelAdmin):
    def save_model(self, request, obj, form, change):
        try:
            upload_bank_records(obj.file.file)
            self.message_user(request, "Záznamy úspěšně nahrány", INFO)
        except AssertionError as e:
            self.message_user(request, str(e), ERROR)

    def response_change(self, request, obj):
        return HttpResponseRedirect(
            reverse("admin:donations_uploadbankrecords_changelist")
        )

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        context["show_save_and_continue"] = False
        context["show_save_and_add_another"] = False
        context["show_delete"] = False
        return super().render_change_form(request, context, add, change, form_url, obj)
