from django.db import models


# Create your models here.
class City(models.Model):
    title = models.CharField(verbose_name="Название города", max_length=60)

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "города"

    def __str__(self):
        return self.title


class District(models.Model):
    title = models.CharField(verbose_name="Название района", max_length=60)
    city = models.ForeignKey(City, verbose_name="Город", on_delete=models.CASCADE, related_name="districts")
    courier = models.ForeignKey(Сourier, verbose_name="Курьер", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Район"
        verbose_name_plural = "Районы"


class Street(models.Model):
    title = models.CharField(verbose_name="Название улицы", max_length=60)
    district = models.ForeignKey(District, verbose_name="Район", on_delete=models.CASCADE, related_name="streets")

    class Meta:
        verbose_name = "Улица"
        verbose_name_plural = "Улицы"


class User(models.Model):
    id = models.CharField(verbose_name="ID пользователя", max_length=255, primary_key=True)

    class Meta:
        verbose_name = "Пользоваетель"
        verbose_name_plural = "Пользователи"


class UserCart(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, related_name="carts")
    price = models.PositiveIntegerField(verbose_name="Итог", default=0)
    address = models.TextField(verbose_name="Адресс", blank=True)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class Category(models.Model):
    title = models.CharField(verbose_name="Название", max_length=100)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(verbose_name="Название", max_length=100)
    price = models.PositiveIntegerField(verbose_name="Цена")
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE, related_name="category")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


class UserPayment(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, related_name="payments")
    cart = models.ForeignKey(UserCart, verbose_name="Корзина", on_delete=models.CASCADE)


class UserProduct(models.Model):
    cart = models.ForeignKey(UserCart, verbose_name="Корзина", on_delete=models.CASCADE, related_name="products")
    product = models.ForeignKey(Product, verbose_name="Продукт", on_delete=models.CASCADE)
    count = models.PositiveIntegerField(verbose_name="Колличество")

    def save(self, *args, **kwargs) -> None:
        cost = self.product.price * self.count
        self.cart.price += cost
        self.cart.save()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Продукт пользователя"
        verbose_name_plural = "Продукты пользователя"
