from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import User, Product, UserCart, City, District, Street, House, UserProduct

from .serializers import (
    UserSerializer,
    ProductSerializer,
    UserCartSerializer,
    CitySerializer,
    DistrictSerializer,
    StreetSerializer,
    HouseSerializer,
    UserProductSerializer,
    UserCartDetailSerializer
)


# Create your views here.
class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, pk=None):
        user = self.get_object()
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CityViewSet(viewsets.GenericViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer 

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
    @action(detail=True, methods=["get"], url_name="districts", url_path="districts", serializer_class=DistrictSerializer, queryset=District.objects.all())
    def districts(self, request, pk=None):
        districts = self.queryset.filter(city_id=pk)
        serializer = self.serializer_class(districts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DistrictViewSet(viewsets.GenericViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer 

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
    @action(detail=True, methods=["get"], url_name="streets", url_path="streets", serializer_class=StreetSerializer, queryset=Street.objects.all())
    def streets(self, request, pk=None):
        streets = self.queryset.filter(district_id=pk)
        serializer = self.serializer_class(streets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StreetViewSet(viewsets.GenericViewSet):
    queryset = Street.objects.all()
    serializer_class = StreetSerializer

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_name="houses", url_path="houses", serializer_class=HouseSerializer, queryset=House.objects.all())
    def houses(self, request, pk=None):
        houses = self.queryset.filter(street_id=pk)
        serializer = self.serializer_class(houses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
