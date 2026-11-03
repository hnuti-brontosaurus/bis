from api.nest_boxes.views import links, public, testing
from api.nest_boxes.views.manage import (
    AreaViewSet,
    BatchViewSet,
    BoxViewSet,
    CheckPhotoViewSet,
    CheckViewSet,
)
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register("public/areas", public.PublicAreaViewSet, "public_areas")
router.register("areas", AreaViewSet, "areas")
router.register("boxes", BoxViewSet, "boxes")
router.register("checks", CheckViewSet, "checks")
router.register("check_photos", CheckPhotoViewSet, "check_photos")
router.register("batches", BatchViewSet, "batches")
router.register("help_articles", public.HelpArticleViewSet, "help_articles")
router.register("help_images", public.HelpImageViewSet, "help_images")

urlpatterns = [
    path("", include(router.urls)),
    path("whoami/", public.WhoAmIView.as_view()),
    path("public/statistics/", public.StatisticsView.as_view()),
    path("public/want_to_hang/", public.WantToHangView.as_view()),
    path("categories/", public.CategoriesView.as_view()),
    path("links/<uuid:token>/", links.LinkView.as_view()),
    path("links/<uuid:token>/checks/", links.LinkChecksView.as_view()),
    path("links/<uuid:token>/boxes/", links.LinkBoxesView.as_view()),
    path("links/<uuid:token>/check_photos/", links.LinkCheckPhotosView.as_view()),
    path("testing/seed/", testing.seed),
]
