from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Account, EmailVerification
from .serializers import SendVerifyCodeSerializer, SignupSerializer, LoginSerializer


class SendVerifyCodeView(viewsets.GenericViewSet,
                         mixins.CreateModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = EmailVerification.objects.all()
    serializer_class = SendVerifyCodeSerializer


class SignupView(viewsets.GenericViewSet,
                 mixins.CreateModelMixin):
    queryset = Account.objects.all()
    serializer_class = SignupSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
