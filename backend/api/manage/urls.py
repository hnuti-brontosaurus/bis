import api.manage.views
from django.urls import path

urlpatterns = [
    path("<str:command>/", api.manage.views.manage),
]
