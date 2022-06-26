import cloudinary
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (Account, EmailVerification)
from .serializers import (SendVerifyCodeSerializer, SignupSerializer, LoginSerializer, SendResetPasswordCodeSerializer,
                          ResetPasswordSerializer, AccountSerializer, UpdateUserProfile,
                          AccountUploadImageSerializer, less_than_2mb)


class SendVerifyCodeView(viewsets.GenericViewSet,
                         mixins.CreateModelMixin):
    queryset = EmailVerification.objects.all()
    serializer_class = SendVerifyCodeSerializer
    permission_classes = [AllowAny]


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

    def get_serializer_class(self):
        if self.action == 'update_profile':
            return UpdateUserProfile
        return AccountSerializer

    @action(detail=False, url_path="me", methods=['Get'])
    def me(self, request):
        serializer = self.get_serializer(self.request.user)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path="me/profile", methods=['Put'])
    def update_profile(self, request):
        instance = self.request.user.user_profile

        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class AccountUploadImage(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Account.objects.all()
    serializer_class = AccountUploadImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


class UploadImage(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Account.objects.all()
    serializer_class = AccountUploadImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        key = list(request.data.keys())[0]
        image = request.data[key]

        if not image:
            return Response(data='image can not be none', status=status.HTTP_404_NOT_FOUND)
        elif not less_than_2mb(image):
            return Response(data='image must be less than 2mb', status=status.HTTP_404_NOT_FOUND)

        cloud = cloudinary.uploader.upload(image, folder="trips/", overwrite=True)

        return Response(data={"image": cloud['url']}, status=status.HTTP_200_OK)
