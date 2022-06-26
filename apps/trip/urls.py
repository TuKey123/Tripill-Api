from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

trip_router = DefaultRouter()
trip_router.register('', views.TripView)

trip_url_patterns = [
    path('', include(trip_router.urls)),
]

album_router = DefaultRouter()
album_router.register('', views.AlbumView)

album_url_patterns = [
    path('', include(album_router.urls)),
]

item_router = DefaultRouter()
item_router.register('', views.ItemViewSet)

item_url_patterns = [
    path('', include(item_router.urls)),
]
