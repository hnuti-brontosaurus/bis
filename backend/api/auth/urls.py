from django.urls import path

import api.auth.views

urlpatterns = [
    path("whoami/", api.auth.views.whoami),
    path("login/", api.auth.views.login),
    path("send_verification_link/", api.auth.views.send_verification_link),
    path("reset_password/", api.auth.views.reset_password),
    path("logout/", api.auth.views.logout),
]
