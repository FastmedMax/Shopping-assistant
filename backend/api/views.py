from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import (
    User,
    Product,
    UserCart,
    City,
    District,
    Street,
    UserProduct,
    Category
)

from .serializers import (
    UserSerializer,
    ProductSerializer,
    UserCartSerializer,
    CitySerializer,
    DistrictSerializer,
    StreetSerializer,
    UserProductSerializer,
    UserCartDetailSerializer,
    CategorySerializer
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


class CategoryViewSet(viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_name="products", url_path="products", serializer_class=ProductSerializer, queryset=Product.objects.all())
    def products(self, request, pk=None):
        products = self.queryset.filter(category_id=pk)
        serializer = self.serializer_class(products, many=True)
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
    

    @action(detail=True, methods=["get"], url_name="courier", url_path="courier")
    def courier(self, request, pk=None):
        district = self.get_object()
        return Response({"courier_id": district.courier.id}, status=status.HTTP_200_OK)


class StreetViewSet(viewsets.GenericViewSet):
    queryset = Street.objects.all()
    serializer_class = StreetSerializer

    def retrieve(self, request, pk=None):
        street = self.get_object()
        serializer = self.serializer_class(street)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCartViewSet(viewsets.GenericViewSet):
    queryset = UserCart.objects.all()
    serializer_class = UserCartSerializer

    def retrieve(self, request, pk=None):
        cart = self.get_object()
        serializer = UserCartDetailSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        cart = self.get_object()
        serializer = self.serializer_class(cart, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=False):
            serializer.update(cart, serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=["post"], url_name="products", url_path="products", serializer_class=UserProductSerializer, queryset=UserProduct.objects.all())
    def products(self, request, pk=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
