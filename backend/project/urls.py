from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from mcp_server.views import MCPServerStreamableHttpView
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.permissions import BasePermission

from bis.views import (
    CodeView,
    LoginView,
    MCPClientRegistrationView,
    OAuthAuthorizationServerMetadataView,
)


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


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
    # OAuth 2.0 Authorization Server Metadata (RFC 8414, required by MCP spec)
    path(
        ".well-known/oauth-authorization-server",
        OAuthAuthorizationServerMetadataView.as_view(),
        name="oauth2_server_metadata",
    ),
    # OAuth2 Provider (django-oauth-toolkit)
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    # Dynamic Client Registration (for MCP clients like Claude AI)
    path("o/register/", MCPClientRegistrationView.as_view(), name="oauth2_dcr"),
    # MCP Server endpoint (superusers only)
    path(
        "mcp",
        MCPServerStreamableHttpView.as_view(
            permission_classes=[IsSuperUser],
            authentication_classes=[OAuth2Authentication],
        ),
        name="mcp_server_streamable_http_endpoint",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
