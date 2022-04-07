from rest_framework import serializers

from .models import Product, UserCart, City, District, Street, House


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class UserCartSelizer(serializers.ModelSerializer):
    class Meta:
        model = UserCart
        fields = "__all__"
        depth = 2


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
