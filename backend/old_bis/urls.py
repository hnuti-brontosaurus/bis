from django.urls import path
from old_bis import views

app_name = "old_bis"

urlpatterns = [
    path("", views.LoginView.as_view(), name="login"),
    path("uvod/", views.WelcomeView.as_view(), name="welcome"),
    path("akce/", views.EventsView.as_view(), name="events"),
    path("akce-na-webu/", views.WebEventsView.as_view(), name="web_events"),
    path("nova-akce/", views.NewEventView.as_view(), name="new_event"),
    path("lokality/", views.LocationsView.as_view(), name="locations"),
    path(
        "zakladni-clanky/",
        views.AdministrationUnitsView.as_view(),
        name="administration_units",
    ),
    path("kluby/", views.SubUnitsView.as_view(), name="sub_units"),
    path("terminy/", views.DashboardItemsView.as_view(), name="dashboard_items"),
    path("hledej/", views.SearchView.as_view(), name="search"),
    path("napoveda/", views.HelpView.as_view(), name="help"),
    path("clenove/", views.MembersView.as_view(), name="members"),
    path("konzultanti-ohb/", views.ConsultantsView.as_view(), name="consultants"),
]
