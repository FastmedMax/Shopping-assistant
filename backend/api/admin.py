from django.contrib import admin

import nested_admin

from .models import (
    Product,
    UserCart,
    City,
    District,
    Street,
    House,
    Сourier,
    User,
    UserProduct,
    Category
)


# Register your models here.
admin.site.register(Сourier)


class ProductsInline(nested_admin.NestedStackedInline):
    model = Product
    extra = 0
    classes = ["collapse"]

@admin.register(Category)
class Category(nested_admin.NestedModelAdmin):
    inlines = (ProductsInline,)


class UserProductsInline(nested_admin.NestedStackedInline):
    model = UserProduct
    extra = 0
    classes = ["collapse"]

class CartInline(nested_admin.NestedStackedInline):
    model = UserCart
    extra = 0
    inlines = (UserProductsInline,)
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
