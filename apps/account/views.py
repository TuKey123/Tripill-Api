from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (Account, EmailVerification)
from .serializers import (SendVerifyCodeSerializer, SignupSerializer, LoginSerializer, SendResetPasswordCodeSerializer,
                          ResetPasswordSerializer, AccountSerializer)


class SendVerifyCodeView(viewsets.GenericViewSet,
                         mixins.CreateModelMixin):
    queryset = EmailVerification.objects.all()
    serializer_class = SendVerifyCodeSerializer


class SignupView(viewsets.GenericViewSet,
                 mixins.CreateModelMixin):
    queryset = Account.objects.all()
    serializer_class = SignupSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class SendResetPasswordCodeView(viewsets.GenericViewSet,
                                mixins.CreateModelMixin):
    queryset = EmailVerification.objects.all()
    serializer_class = SendResetPasswordCodeSerializer


class ResetPasswordView(viewsets.GenericViewSet,
                        mixins.CreateModelMixin):
    queryset = Account.objects.all()
    serializer_class = ResetPasswordSerializer


class AccountView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, url_path="me", methods=['Get'])
    def me(self, request):
        serializer = self.get_serializer(self.request.user)

        return Response(data=serializer.data, status=status.HTTP_200_OK)
