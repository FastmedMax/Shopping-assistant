from rest_framework import serializers

from .models import User, Product, UserCart, City, District, Street, House, UserProduct


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class UserCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCart
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"


class StreetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Street
        fields = "__all__"


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = "__all__"


class UserProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProduct
        fields = "__all__"


class UserProductDetailSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(slug_field="title", read_only=True)
    class Meta:
        model = UserProduct
        exclude = ("cart", "id")


class UserCartDetailSerializer(serializers.ModelSerializer):
    products = UserProductDetailSerializer(many=True)
    class Meta:
        model = UserCart
        exclude = ("id", "user")
