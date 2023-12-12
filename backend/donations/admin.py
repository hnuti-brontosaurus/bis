from admin_auto_filters.filters import AutocompleteFilterFactory
from admin_numeric_filter.admin import RangeNumericFilter
from bis.admin_filters import (
    DonationSumAmountFilter,
    DonationSumRangeFilter,
    FirstDonorsDonationFilter,
    HasDonorFilter,
    LastDonorsDonationFilter,
    RecurringDonorWhoStoppedFilter,
)
from bis.admin_permissions import PermissionMixin
from django.contrib.messages import ERROR, INFO
from django.http import HttpResponseRedirect
from django.urls import reverse
from donations.helpers import upload_bank_records
from donations.models import Donation, Donor, UploadBankRecords, VariableSymbol
from event.models import *
from more_admin_filters import MultiSelectRelatedDropdownFilter
from nested_admin.nested import NestedModelAdmin, NestedTabularInline
from rangefilter.filters import DateRangeFilter
from solo.admin import SingletonModelAdmin
from xlsx_export.export import export_to_xlsx


@admin.register(Donation)
class DonationAdmin(PermissionMixin, NestedModelAdmin):
    actions = [export_to_xlsx]
    autocomplete_fields = ("donor",)
    list_display = "__str__", "donor", "donated_at", "donation_source", "info"
    list_filter = (
        ("amount", RangeNumericFilter),
        ("donated_at", DateRangeFilter),
        HasDonorFilter,
        ("donation_source", MultiSelectRelatedDropdownFilter),
    )
    exclude = "_import_id", "_variable_symbol"

    list_select_related = "donor__user", "donation_source"
    search_fields = (
        "donor__user__all_emails__email",
        "donor__user__phone",
        "donor__user__first_name",
        "donor__user__last_name",
        "donor__user__nickname",
        "donor__user__birth_name",
    )


class DonationAdminInline(PermissionMixin, NestedTabularInline):
    model = Donation


class VariableSymbolInline(PermissionMixin, NestedTabularInline):
    model = VariableSymbol
    extra = 0


@admin.register(Donor)
class DonorAdmin(PermissionMixin, NestedModelAdmin):
    actions = [export_to_xlsx]
    list_display = (
        "user",
        "get_user_email",
        "get_user_phone",
        "get_user_pronoun",
        "date_joined",
        "get_donations_sum",
        "get_last_donation",
        "get_donations_sources",
        "regional_center_support",
        "basic_section_support",
        "subscribed_to_newsletter",
        "is_public",
    )

    list_select_related = (
        "user",
        "user__pronoun",
        "regional_center_support",
        "basic_section_support",
    )
    inlines = (
        VariableSymbolInline,
        DonationAdminInline,
    )
    search_fields = (
        "user__all_emails__email",
        "user__phone",
        "user__first_name",
        "user__last_name",
        "user__nickname",
        "user__birth_name",
    )
    list_filter = (
        "user__pronoun",
        ("user__roles", MultiSelectRelatedDropdownFilter),
        "subscribed_to_newsletter",
        "is_public",
        "has_recurrent_donation",
        AutocompleteFilterFactory("Podporující RC", "regional_center_support"),
        AutocompleteFilterFactory("Podporující ZČ", "basic_section_support"),
        ("donations__donation_source", MultiSelectRelatedDropdownFilter),
        ("donations__donated_at", FirstDonorsDonationFilter),
        ("donations__donated_at", LastDonorsDonationFilter),
        ("donations__donated_at", DonationSumRangeFilter),
        ("donations__amount", DonationSumAmountFilter),
        RecurringDonorWhoStoppedFilter,
    )

    autocomplete_fields = "regional_center_support", "basic_section_support", "user"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return "user", "get_donations_sum"
        return ("get_donations_sum",)

    def save_formset(self, request, form, formset, change):
        if formset.model is Donation:
            formset.new_objects = []
            formset.changed_objects = []
            formset.deleted_objects = []
            return
        super().save_formset(request, form, formset, change)

    def get_queryset(self, request):
        return (
            super().get_queryset(request).prefetch_related("donations__donation_source")
        )

    @admin.display(description="Suma darů")
    def get_donations_sum(self, obj):
        return sum([donation.amount for donation in obj.donations.all()])

    @admin.display(description="Poslední dar")
    def get_last_donation(self, obj):
        if obj.donations.all():
            return list(obj.donations.all())[-1].donated_at

    @admin.display(description="E-mail")
    def get_user_email(self, obj):
        return obj.user.email

    @admin.display(description="Telefon")
    def get_user_phone(self, obj):
        return obj.user.phone

    @admin.display(description="Oslovení")
    def get_user_pronoun(self, obj):
        return obj.user.pronoun

    @admin.display(description="Darovací kampaně")
    def get_donations_sources(self, obj):
        return list(set(donation.donation_source for donation in obj.donations.all()))


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
