from apps.account.urls import url_patterns as auth_urls
from django.urls import path, include

url_patterns = [
    path('auth/', include(auth_urls)),
    path('user/', include(auth_urls)),
]
