from apps.account.urls import auth_url_patterns, account_url_patterns, upload_image_patterns
from apps.trip.urls import trip_url_patterns, album_url_patterns, item_url_patterns
from django.urls import path, include

url_patterns = [
    path('auth/', include(auth_url_patterns)),
    path('users/', include(account_url_patterns)),
    path('upload-image/', include(upload_image_patterns)),
    path('trips/', include(trip_url_patterns)),
    path('items/', include(item_url_patterns)),
    path('albums/', include(album_url_patterns)),
]
