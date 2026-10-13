from administration_units.models import AdministrationSubUnit, AdministrationUnit
from bis.models import Location, Qualification, User
from bis.permissions import Permissions
from dateutil.utils import today
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from event.models import Event
from other.models import Announcement, DashboardItem
from unidecode import unidecode


class LoginView(TemplateView):
    template_name = "old_bis/login.html"
    extra_context = {"api_base": settings.API_BASE}


class OldBisView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy("old_bis:login")

    def visible(self, model):
        return Permissions(self.request.user, model, "frontend").filter_queryset(
            model.objects.all()
        )

    def paginate(self, queryset):
        page = Paginator(queryset, 20).get_page(self.request.GET.get("strana"))
        return {
            "page": page,
            "page_range": page.paginator.get_elided_page_range(page.number),
        }


class WelcomeView(OldBisView):
    template_name = "old_bis/welcome.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            announcements=Announcement.get_current_for_user(self.request.user),
            dashboard_items=DashboardItem.get_items_for_user(self.request.user)[:10],
            **kwargs,
        )


class EventListView(OldBisView):
    orderings = {"nazev": "name", "od": "start"}

    def get_context_data(self, **kwargs):
        sort = self.request.GET.get("sort")
        events = self.get_events().select_related(
            "location", "group", "category", "program", "intended_for"
        )
        events = events.order_by(self.orderings.get(sort, "-start"))
        return super().get_context_data(
            **self.paginate(events),
            sort=sort or "",
            today=today().date(),
            **kwargs,
        )


class EventsView(EventListView):
    template_name = "old_bis/events.html"

    def get_events(self):
        return self.visible(Event).select_related("propagation", "record")


class WebEventsView(EventListView):
    template_name = "old_bis/web_events.html"

    def get_events(self):
        return Event.objects.filter(
            propagation__is_shown_on_web=True, is_canceled=False
        )


class NewEventView(OldBisView):
    template_name = "old_bis/new_event.html"


class LocationsView(OldBisView):
    template_name = "old_bis/locations.html"

    def get_context_data(self, **kwargs):
        locations = self.visible(Location).select_related("region", "patron")
        return super().get_context_data(**self.paginate(locations), **kwargs)


class AdministrationUnitsView(OldBisView):
    template_name = "old_bis/units.html"

    def get_context_data(self, **kwargs):
        units = self.visible(AdministrationUnit).select_related("address", "chairman")
        if self.request.GET.get("filter") != "all":
            units = units.filter(existed_till=None)
        return super().get_context_data(
            title="Základní články",
            units=[{"unit": unit, "leader": unit.chairman} for unit in units],
            **kwargs,
        )


class SubUnitsView(OldBisView):
    template_name = "old_bis/units.html"

    def get_context_data(self, **kwargs):
        sub_units = self.visible(AdministrationSubUnit).select_related(
            "address", "main_leader"
        )
        if self.request.GET.get("filter") != "all":
            sub_units = sub_units.filter(is_active=True)
        return super().get_context_data(
            title="Kluby",
            units=[
                {"unit": sub_unit, "leader": sub_unit.main_leader}
                for sub_unit in sub_units
            ],
            **kwargs,
        )


class DashboardItemsView(OldBisView):
    template_name = "old_bis/dashboard_items.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            dashboard_items=DashboardItem.get_items_for_user(self.request.user),
            **kwargs,
        )


class ConsultantsView(OldBisView):
    template_name = "old_bis/consultants.html"
    validities = {"propadla": "expired", "vsi": "all"}

    def get_context_data(self, **kwargs):
        validity = self.validities.get(
            self.request.GET.get("filter_platnost"), "current"
        )
        qualifications = Qualification.objects.filter(
            category__slug__in=["consultant", "consultant_for_kids"],
            user__in=self.visible(User),
        ).select_related("user", "category")
        if validity == "current":
            qualifications = qualifications.filter(valid_till__gte=today())
        if validity == "expired":
            qualifications = qualifications.filter(valid_till__lt=today())
        return super().get_context_data(
            validity=validity,
            qualifications=qualifications.order_by(
                "user__last_name", "user__first_name"
            ),
            **kwargs,
        )


class SearchView(OldBisView):
    template_name = "old_bis/search.html"

    def get_context_data(self, **kwargs):
        pattern = self.request.GET.get("pattern", "").strip()
        users = None
        if pattern:
            users = self.visible(User).filter(
                _search_field__icontains=unidecode(pattern)
            )[:100]
        return super().get_context_data(pattern=pattern, users=users, **kwargs)


class HelpView(OldBisView):
    template_name = "old_bis/help.html"


class MembersView(OldBisView):
    template_name = "old_bis/members.html"
