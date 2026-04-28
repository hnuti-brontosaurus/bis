from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.contrib.messages import ERROR, INFO
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Exists, Max, Min, OuterRef, Q
from django.http import FileResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html
from more_admin_filters import MultiSelectRelatedDropdownFilter
from nested_admin.nested import NestedModelAdmin, NestedTabularInline
from rangefilter.filters import DateRangeFilter
from solo.admin import SingletonModelAdmin

from bis.admin_filters import (
    DonationSumAmountFilter,
    DonationSumRangeFilter,
    FirstDonorsDonationFilter,
    HasDonorFilter,
    HasPledgeInCampaignFilter,
    HasRecurrentDonationFilter,
    LastDonorsDonationFilter,
    MultiSelectRelatedDropdownAndCampaignFilter,
    RecurringDonorWhoStoppedFilter,
)
from bis.admin_helpers import (
    ListAwareRangeNumericFilter,
    list_filter_extra_note,
    list_filter_extra_title,
)
from bis.admin_permissions import PermissionMixin
from bis.emails import donation_confirmation
from bis.permissions import Permissions
from categories.models import DonorEventCategory, PronounCategory
from donations.helpers import upload_bank_records
from donations.models import (
    Company,
    Donation,
    Donor,
    DonorEvent,
    FundraisingCampaign,
    Pledge,
    UploadBankRecords,
    VariableSymbol,
)
from bis.models import User
from xlsx_export.export import export_to_xlsx, get_donation_confirmation


@admin.register(FundraisingCampaign)
class FundraisingCampaignAdmin(PermissionMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "telesales_link")

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

        def call(request, campaign_id, donor_id):
            return telesales_call_view(self, request, campaign_id, donor_id)

        custom = [
            path(
                "telesales/<int:campaign_id>/",
                self.admin_site.admin_view(worklist_campaign),
                name="donations_telesales_worklist",
            ),
            path(
                "telesales/<int:campaign_id>/call/<int:donor_id>/",
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


class DonationAdminInline(PermissionMixin, NestedTabularInline):
    model = Donation
    exclude = ("_variable_symbol", "_import_id", "pledge")


class VariableSymbolInline(PermissionMixin, NestedTabularInline):
    model = VariableSymbol
    extra = 0


class CompanyInline(PermissionMixin, NestedTabularInline):
    model = Company
    extra = 0


class DonorEventAdminInline(PermissionMixin, NestedTabularInline):
    model = DonorEvent
    extra = 0
    readonly_fields = ("created_at", "created_by")
    fields = (
        "event_type",
        "campaign",
        "fundraisers_note",
        "pledge",
        "reminder",
        "created_at",
        "created_by",
    )


def mark_with_pronoun(model_admin, request, queryset, pronoun):
    perms = Permissions(request.user, Donor, "backend")
    if not all([perms.has_change_permission(obj) for obj in queryset]):
        return model_admin.message_user(
            request, "Nemáš právo editovat vybrané objekty", ERROR
        )
    users = User.objects.filter(id__in=queryset.values_list("user_id"))
    users.update(pronoun=pronoun)


@admin.action(description="Označ vybrané mužským oslovením")
def mark_as_man(model_admin, request, queryset):
    mark_with_pronoun(
        model_admin, request, queryset, PronounCategory.objects.get(slug="man")
    )


@admin.action(description="Označ vybrané ženským oslovením")
def mark_as_woman(model_admin, request, queryset):
    mark_with_pronoun(
        model_admin, request, queryset, PronounCategory.objects.get(slug="woman")
    )


@admin.action(description="Zašli potvrzení o daru")
def send_donation_confirmation(model_admin, request, queryset):
    perms = Permissions(request.user, Donor, "backend")
    if not all([perms.has_change_permission(obj) for obj in queryset]):
        return model_admin.message_user(
            request, "Nemáš právo editovat vybrané objekty", ERROR
        )
    i = 0
    for obj in queryset:
        try:
            donation_confirmation(obj, *get_donation_confirmation(obj))
            i += 1
        except AssertionError as e:
            messages.error(request, str(e))
    messages.info(request, f"Úspěšně posláno {i} potvrzení")


CAMPAIGN_OPERATIONS = [
    ("added_to_campaign", "Přidat do kampaně"),
    ("remove", "Odebrat z kampaně"),
]


@admin.action(description="Změň členství v fundraisingové kampani…")
def change_fundraising_campaign(model_admin, request, queryset):
    if "apply" in request.POST:
        campaign_id = request.POST.get("campaign")
        operation_slug = request.POST.get("operation")

        try:
            campaign = FundraisingCampaign.objects.get(pk=campaign_id)
        except FundraisingCampaign.DoesNotExist:
            messages.error(request, "Vyberte kampaň.")
            return

        if operation_slug not in dict(CAMPAIGN_OPERATIONS):
            messages.error(request, "Vyberte operaci.")
            return

        added_type = DonorEventCategory.objects.get(slug="added_to_campaign")

        count = 0
        for donor in queryset:
            membership_qs = DonorEvent.objects.filter(
                donor=donor, campaign=campaign, event_type=added_type
            )
            if operation_slug == "added_to_campaign":
                if not membership_qs.exists():
                    DonorEvent.objects.create(
                        donor=donor,
                        event_type=added_type,
                        campaign=campaign,
                        created_by=request.user,
                    )
                    count += 1
            else:
                membership = membership_qs.first()
                if membership:
                    other_events = DonorEvent.objects.filter(
                        donor=donor, campaign=campaign
                    ).exclude(pk=membership.pk)
                    if not other_events.exists():
                        membership.delete()
                        count += 1

        messages.success(
            request, f"Provedeno pro {count} dárce/dárců v kampani {campaign}."
        )
        return

    return TemplateResponse(
        request,
        "donations/campaign_action.html",
        {
            "title": "Změnit členství v fundraisingové kampani",
            "queryset": queryset,
            "campaigns": FundraisingCampaign.objects.all(),
            "operations": CAMPAIGN_OPERATIONS,
            "action_name": "change_fundraising_campaign",
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "opts": model_admin.model._meta,
        },
    )


@admin.register(Donor)
class DonorAdmin(PermissionMixin, NestedModelAdmin):
    change_form_template = "bis/donor_change_form.html"
    actions = [
        send_donation_confirmation,
        mark_as_woman,
        mark_as_man,
        export_to_xlsx,
        change_fundraising_campaign,
    ]
    list_display = (
        "user",
        "get_user_email",
        "get_user_phone",
        "formal_vokativ",
        "get_user_pronoun",
        "date_joined",
        "get_donations_sum",
        "get_last_donation",
        "get_donations_sources",
        "has_active_recurrent_donation_display",
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
        CompanyInline,
        VariableSymbolInline,
        DonationAdminInline,
        DonorEventAdminInline,
    )
    search_fields = User.get_search_fields(prefix="user__")
    list_filter = (
        "user__pronoun",
        ("user__roles", MultiSelectRelatedDropdownFilter),
        "subscribed_to_newsletter",
        "is_public",
        HasRecurrentDonationFilter,
        AutocompleteFilterFactory("Podporující RC", "regional_center_support"),
        AutocompleteFilterFactory("Podporující ZČ", "basic_section_support"),
        list_filter_extra_title("Dary"),
        ("donations__donation_source", MultiSelectRelatedDropdownFilter),
        list_filter_extra_note("Dary jen z vybraných zdrojů"),
        ("donations__donated_at", FirstDonorsDonationFilter),
        list_filter_extra_note("První dan dárce (z vybraných zdrojů) z daného období"),
        ("donations__donated_at", LastDonorsDonationFilter),
        list_filter_extra_note(
            "Poslední dan dárce (z vybraných zdrojů) z daného období"
        ),
        ("donations__donated_at", DonationSumRangeFilter),
        list_filter_extra_note(
            "Dary pro celkovou sumu (z vybraných zdrojů) jen z daného období"
        ),
        ("donations__amount", DonationSumAmountFilter),
        list_filter_extra_note(
            "Suma darů (z vybraných zdrojů) (z vybraného období) z daného rozmezí"
        ),
        RecurringDonorWhoStoppedFilter,
        list_filter_extra_title("Fundraisingové kampaně"),
        ("events__campaign", MultiSelectRelatedDropdownFilter),
        ("events__event_type", MultiSelectRelatedDropdownAndCampaignFilter),
        HasPledgeInCampaignFilter,
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
        queryset = (
            super().get_queryset(request).prefetch_related("donations__donation_source")
        )
        active_recurrent_pledges = Pledge.objects.filter(
            donor=OuterRef("pk"), is_recurrent=True, recurrent_state="collecting"
        )
        queryset = queryset.annotate(
            has_active_recurrent_donation=Exists(active_recurrent_pledges)
        )

        past_recurrent_pledges = Pledge.objects.filter(
            donor=OuterRef("pk"), is_recurrent=True, recurrent_state="stopped"
        )
        queryset = queryset.annotate(
            had_recurrent_donation=Exists(past_recurrent_pledges)
        )

        donations_source_filter = MultiSelectRelatedDropdownFilter(
            field=Donation.donation_source.field,
            request=request,
            params=dict(request.GET.items()),
            model=self.model,
            model_admin=self,
            field_path="donations__donation_source",
        )
        annotate_filter = None
        if source_ids := donations_source_filter.used_parameters.values():
            source_ids = list(source_ids)[0]
            annotate_filter = Q(donations__donation_source_id__in=source_ids)

        queryset = queryset.annotate(
            first_donation=Min("donations__donated_at", filter=annotate_filter)
        )
        queryset = queryset.annotate(
            last_donation=Max("donations__donated_at", filter=annotate_filter)
        )
        queryset = queryset.annotate(
            donation_sources=ArrayAgg(
                "donations__donation_source__name",
                distinct=True,
                filter=annotate_filter,
            )
        )
        donations_sum_filter = DonationSumRangeFilter(
            field=Donation.donated_at,
            request=request,
            params=dict(request.GET.items()),
            model=self.model,
            model_admin=self,
            field_path="donations__donated_at",
        )
        return donations_sum_filter.annotate(request, queryset, annotate_filter)

    @admin.display(description="Suma darů")
    def get_donations_sum(self, obj):
        return obj.donations_sum

    @admin.display(description="Poslední dar")
    def get_last_donation(self, obj):
        return obj.last_donation

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
        return obj.donation_sources

    @admin.display(description="Pravidelný dárce", boolean=True)
    def has_active_recurrent_donation_display(self, obj):
        return obj.has_active_recurrent_donation

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if object_id:
            to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
            obj = self.get_object(request, unquote(object_id), to_field)

            try:
                if "_donation_confirmation_pdf_export" in request.POST:
                    return FileResponse(
                        get_donation_confirmation(obj)[0], as_attachment=True
                    )
                if "_donation_confirmation_pdf_email" in request.POST:
                    donation_confirmation(obj, *get_donation_confirmation(obj))
                    messages.info(request, "Potvrzení o daru úspěšně odesláno")
            except AssertionError as e:
                messages.error(request, str(e))

        return super().changeform_view(request, object_id, form_url, extra_context)


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
