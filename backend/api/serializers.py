from rest_framework import serializers

from .models import Product, UserCart, City, District, Street, House


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
