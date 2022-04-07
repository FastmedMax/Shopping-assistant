from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Product, UserCart, City, District, Street, House

from .serializers import ProductSerializer, UserCartSelizer, CitySerializer, DistrictSerializer, StreetSerializer, HouseSerializer


# Create your views here.
