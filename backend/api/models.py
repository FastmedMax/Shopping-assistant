from django.db import models


# Create your models here.
class Сourier(models.Model):
    id = models.CharField(verbose_name="ID курьера", max_length=255, primary_key=True)

