from django.db import models


# Create your models here.
class Сourier(models.Model):
    id = models.CharField(verbose_name="ID курьера", max_length=255, primary_key=True)


class City(models.Model):
    title = models.CharField(verbose_name="Название города", max_length=60)


class District(models.Model):
    title = models.CharField(verbose_name="Название района", max_length=60)
    city = models.ForeignKey(City, verbose_name="Город", on_delete=models.CASCADE, related_name="districts")
    courier = models.ForeignKey(Сourier, verbose_name="Курьер", on_delete=models.CASCADE)


class Street(models.Model):
    title = models.CharField(verbose_name="Название улицы", max_length=60)
    district = models.ForeignKey(City, verbose_name="Район", on_delete=models.CASCADE, related_name="streets")


class House(models.Model):
    title = models.CharField(verbose_name="Название дома", max_length=60)
    street = models.ForeignKey(City, verbose_name="Улица", on_delete=models.CASCADE, related_name="houses")


class User(models.Model):
    id = models.CharField(verbose_name="ID курьера", max_length=255, primary_key=True)


class UserCart(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, related_name="carts")
    price = models.PositiveIntegerField(verbose_name="Итог")
    address = models.TextField(verbose_name="Адресс")


class Product(models.Model):
    title = models.CharField(verbose_name="Название", max_length=100)
    price = models.PositiveIntegerField(verbose_name="Цена")


class UserPayment(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, related_name="payments")
    cart = models.ForeignKey(UserCart, verbose_name="Корзина", on_delete=models.CASCADE)


class UserProduct(models.Model):
    cart = models.ForeignKey(UserCart, verbose_name="Корзина", on_delete=models.CASCADE, related_name="products")
    product = models.ForeignKey(Product, verbose_name="Продукт", on_delete=models.CASCADE)
    count = models.PositiveIntegerField(verbose_name="Колличество")
