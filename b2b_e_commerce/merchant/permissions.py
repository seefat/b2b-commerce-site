from rest_framework import permissions
from .models import Shop


class IsMerchantShop(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        shop_slug = view.kwargs.get('shop_slug')  # Assumes the URL parameter is named 'shop_id'
        try:
            shop = Shop.objects.get(slug=shop_slug)
        except Shop.DoesNotExist:
            return False
 # Chreturn eck if the logged-in merchant is associated with the shop
        merchant = request.user
        return merchant.is_authenticated and shop.merchant == merchant
