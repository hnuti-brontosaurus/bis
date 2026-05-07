from api.cookbook.serializers import CartSerializer
from cookbook.models.cart import Cart
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated


class CartViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """Singleton cart per authenticated user.

    Routed at /cart/ (no pk) — `get_object` always returns the requester's
    own cart, auto-creating it on first access.
    """

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    http_method_names = ["get", "patch", "options", "head"]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart
