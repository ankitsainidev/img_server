from django.db import models
from django.conf import settings

# Create your models here.
class Client(models.Model):
    user = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    thumbs = models.CharField(max_length = 10) 