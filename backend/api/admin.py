from django.contrib import admin

import nested_admin

from .models import Product, UserCart, City, District, Street, House, Сourier, User, UserProduct


# Register your models here.
admin.site.register(Product)
admin.site.register(Сourier)


class ProductsInline(nested_admin.NestedStackedInline):
    model = UserProduct
    extra = 0
    classes = ["collapse"]

class CartInline(nested_admin.NestedStackedInline):
    model = UserCart
    extra = 0
    inlines = (ProductsInline,)
    classes = ["collapse"]

@admin.register(User)
class User(nested_admin.NestedModelAdmin):
    inlines = (CartInline,)


class HouseInline(nested_admin.NestedStackedInline):
    model = House
    extra = 0
    classes = ["collapse"]

class StreetInline(nested_admin.NestedStackedInline):
    model = Street
    extra = 0
    classes = ["collapse"]
    inlines = (HouseInline,)

class DistrictInline(nested_admin.NestedStackedInline):
    model = District
    extra = 0
    classes = ["collapse"]
    inlines = (StreetInline,)

@admin.register(City)
class User(nested_admin.NestedModelAdmin):
    inlines = (DistrictInline,)
