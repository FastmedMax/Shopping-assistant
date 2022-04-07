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
