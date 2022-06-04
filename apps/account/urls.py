from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

auth_router = DefaultRouter()
auth_router.register('send-verify-code', views.SendVerifyCodeView)
auth_router.register('sign-up', views.SignupView)
auth_router.register('send-reset-password-code', views.SendResetPasswordCodeView)
auth_router.register('reset-password', views.ResetPasswordView)

auth_url_patterns = [
    path('', include(auth_router.urls)),
    path('login/', views.LoginView.as_view()),
    path('token-refresh/', TokenRefreshView.as_view()),
]

account_router = DefaultRouter()
account_router.register('', views.AccountView)

account_url_patterns = [
    path('', include(account_router.urls)),
]
