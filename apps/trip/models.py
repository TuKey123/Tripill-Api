from django.db import models

from apps.account.models import Account


class Album(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="albums")

    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Trip(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="trips")
    collaborators = models.ManyToManyField(Account, null=True, blank=True, related_name="collaborate_trips")
    album = models.ForeignKey(Album, null=True, blank=True, on_delete=models.CASCADE, related_name="trips")

    name = models.CharField(max_length=256)
    location = models.CharField(max_length=256)
    image = models.ImageField(upload_to='trips/', null=True, blank=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='items')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subs')

    lat = models.CharField(max_length=256)
    lng = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    is_single = models.BooleanField(default=True)
    image = models.CharField(max_length=256, null=True, blank=True)
