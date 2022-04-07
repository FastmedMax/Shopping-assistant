from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, CityViewSet, DistrictViewSet, StreetViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="products")
router.register(r"cities", CityViewSet, basename="cities")
router.register(r"districts", DistrictViewSet, basename="districts")
router.register(r"streets", StreetViewSet, basename="streets")

urlpatterns = [
] + router.urls