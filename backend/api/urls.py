from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("auth/", include("api.auth.urls")),
    path("web/", include("api.web.urls")),
    path("categories/", include("api.categories.urls")),
    path("cookbook/", include("api.cookbook.urls")),
    path("frontend/", include("api.frontend.urls")),
    path("manage/", include("api.manage.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
