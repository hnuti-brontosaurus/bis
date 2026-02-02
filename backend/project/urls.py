from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from oauth_dcr.views import DynamicClientRegistrationView

from bis.views import CodeView, LoginView

urlpatterns = [
    # custom authentication
    path("admin/login/", RedirectView.as_view(url="/logout", query_string=True)),
    path("admin/logout/", RedirectView.as_view(url="/logout", query_string=True)),
    path("admin/bis/event/add/", RedirectView.as_view(url="/org/akce/vytvorit")),
    path(
        "admin/opportunities/opportunity/add/",
        RedirectView.as_view(url="/org/prilezitosti/vytvorit"),
    ),
    path("admin/code_login/", LoginView.as_view()),
    path("enter_code/", CodeView.as_view(), name="code"),
    path("admin/", admin.site.urls),
    path(f"_rest_framework/", include("rest_framework.urls")),
    path(f"_nested_admin/", include("nested_admin.urls")),
    path("tinymce/", include("tinymce.urls")),
    path(f"{settings.API_BASE}", include("api.urls")),
    path(f"game_book/", include("game_book.urls")),
    # OAuth2 Provider (django-oauth-toolkit)
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    # Dynamic Client Registration (for Claude AI)
    path("o/register/", DynamicClientRegistrationView.as_view(), name="oauth2_dcr"),
    # MCP Server endpoint
    path("", include("mcp_server.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
