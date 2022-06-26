from django.db import models
from datetime import datetime
from apps.account.models import Account


class Album(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="albums")

    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Trip(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="trips")
    collaborators = models.ManyToManyField(Account, null=True, blank=True, related_name="collaborate_trips")
    album = models.ForeignKey(Album, null=True, blank=True, on_delete=models.SET_NULL, related_name="trips")

    name = models.CharField(max_length=256)
    location = models.CharField(max_length=256)
    description = models.CharField(max_length=512, null=True, blank=True)
    image = models.CharField(max_length=256, null=True, blank=True)
    start_date = models.DateTimeField(default=datetime.now(), null=False)
    end_date = models.DateTimeField(default=datetime.now(), null=False)

    def __str__(self):
        return self.name


class Item(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='items')

    lat = models.FloatField()
    lng = models.FloatField()
    location = models.CharField(max_length=256)
    description = models.CharField(max_length=512, null=True, blank=True)
    image = models.CharField(max_length=256, null=True, blank=True)
    start_date = models.DateTimeField(default=datetime.now())
    end_date = models.DateTimeField(default=datetime.now())
    note = models.JSONField(null=True)
    is_shared = models.BooleanField(default=False)


class AppreciatedTrip(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="appreciated_trips")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='appreciated_users')


class AppreciatedItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="appreciated_items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='appreciated_users')
