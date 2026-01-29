from django.urls import path

import api.manage.views

urlpatterns = [
    path("command/<str:command>/", api.manage.views.manage),
    path(
        "resize_event_photos/<int:event_id>/<str:size>/",
        api.manage.views.resize_event_photos,
    ),
]
