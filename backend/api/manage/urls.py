from django.urls import path

import api.manage.views

urlpatterns = [
    path('<str:command>/', api.manage.views.manage),
]
