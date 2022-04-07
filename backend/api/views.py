from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Product, UserCart, City, District, Street, House

from .serializers import ProductSerializer, UserCartSelizer, CitySerializer, DistrictSerializer, StreetSerializer, HouseSerializer


# Create your views here.
class ProductViewSet(viewsets.GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
