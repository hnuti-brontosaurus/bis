from bis.views import (
    MCPClientRegistrationView,
    OAuthAuthorizationServerMetadataView,
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from mcp_server.views import MCPServerStreamableHttpView
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.permissions import BasePermission

BRONTOBOT_EMAIL = "brontosaurus.bot@gmail.com"


class MCPPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.is_staff or user.email == BRONTOBOT_EMAIL


urlpatterns = [
    # custom authentication
    path("admin/login/", RedirectView.as_view(url="/logout", query_string=True)),
    path("admin/logout/", RedirectView.as_view(url="/logout", query_string=True)),
    path("admin/bis/event/add/", RedirectView.as_view(url="/org/akce/vytvorit")),
    path(
        "admin/opportunities/opportunity/add/",
        RedirectView.as_view(url="/org/prilezitosti/vytvorit"),
    ),
    path("admin/", admin.site.urls),
    path("_rest_framework/", include("rest_framework.urls")),
    path("_nested_admin/", include("nested_admin.urls")),
    path("tinymce/", include("tinymce.urls")),
    path(f"{settings.API_BASE}", include("api.urls")),
    path("game_book/", include("game_book.urls")),
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
            permission_classes=[MCPPermission],
            authentication_classes=[OAuth2Authentication],
        ),
        name="mcp_server_streamable_http_endpoint",
    ),
]

if settings.ENVIRONMENT in ("local", "testing"):
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
