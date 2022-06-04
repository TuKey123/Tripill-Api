from django.contrib import admin
from apps.trip.models import Album, Trip, Item

# Register your models here.
admin.site.register(Album)
admin.site.register(Trip)
admin.site.register(Item)
