from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Folder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    size = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}"


class Place(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    location = models.CharField(max_length=1024)
    category = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name="cat")
    un = models.CharField(max_length=64)
    pw = models.BinaryField(max_length=128)

    def __str__(self):
        return f"{self.name}"
