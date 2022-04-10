from django.contrib import admin

import nested_admin

from .models import Product, UserCart, City, District, Street, House, Сourier, User, UserProduct


# Register your models here.
admin.site.register(Product)
admin.site.register(UserCart)
admin.site.register(City)
admin.site.register(District)
admin.site.register(Street)
admin.site.register(House)
admin.site.register(Сourier)
