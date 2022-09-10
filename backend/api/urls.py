from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path(f'auth/', include('api.auth.urls')),
    path(f'web/', include('api.web.urls')),
    path(f'categories/', include('api.categories.urls')),
    path(f'frontend/', include('api.frontend.urls')),

    path(f'schema/', SpectacularAPIView.as_view(), name='schema'),
    path(f'', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
