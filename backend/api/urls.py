from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    CategoryViewSet,
    CityViewSet,
    DistrictViewSet,
    StreetViewSet,
    UserCartViewSet
)

app_name = 'api'

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"cities", CityViewSet, basename="cities")
router.register(r"districts", DistrictViewSet, basename="districts")
router.register(r"streets", StreetViewSet, basename="streets")
router.register(r"cart", UserCartViewSet, basename="cart")

urlpatterns = [
] + router.urls