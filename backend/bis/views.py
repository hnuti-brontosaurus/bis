from django.conf import settings
from django.http import JsonResponse
from django.views import View
from oauth_dcr.views import DynamicClientRegistrationView


class MCPClientRegistrationView(DynamicClientRegistrationView):
    """DCR override that forces public clients (PKCE).

    MCP clients like Claude.ai are public clients using PKCE,
    so token_endpoint_auth_method must be "none".
    """

    def _validate_client_metadata(self, metadata):
        metadata["token_endpoint_auth_method"] = "none"
        return super()._validate_client_metadata(metadata)


class OAuthAuthorizationServerMetadataView(View):
    """RFC 8414 OAuth 2.0 Authorization Server Metadata endpoint.

    Required by the MCP protocol for Claude.ai and other MCP clients
    to discover OAuth endpoints.
    """

    def get(self, request):
        issuer = settings.FULL_HOSTNAME
        return JsonResponse(
            {
                "issuer": issuer,
                "authorization_endpoint": f"{issuer}/o/authorize/",
                "token_endpoint": f"{issuer}/o/token/",
                "registration_endpoint": f"{issuer}/o/register/",
                "scopes_supported": list(
                    settings.OAUTH2_PROVIDER.get("SCOPES", {}).keys()
                ),
                "response_types_supported": ["code"],
                "grant_types_supported": ["authorization_code"],
                "code_challenge_methods_supported": ["S256"],
                "token_endpoint_auth_methods_supported": ["none"],
            },
            headers={"Access-Control-Allow-Origin": "*"},
        )
