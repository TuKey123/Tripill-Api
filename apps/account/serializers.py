from django.core.mail import send_mail
from rest_framework import serializers
from django.conf import settings
from datetime import datetime, timedelta
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import EmailVerification, Account, UserProfile
from ..trip.models import Trip, Album

import random


# EXTRA FUNC
def less_than_2mb(image):
    # convert to Mb
    size = image.size / (1024 ** 2)

    if size > 2:
        return False
    return True


def create_verification_record(email):
    verify_code = random.randint(10 ** (settings.VERIFY_CODE_LENGTH - 1), 10 ** settings.VERIFY_CODE_LENGTH - 1)
    expired_day = datetime.now() + timedelta(hours=settings.VERIFY_CODE_EXPIRED_HOURS)

    (instance, _) = EmailVerification.objects.update_or_create(email=email, defaults={'verify_code': verify_code,
                                                                                      'expired_day': expired_day})

    return instance


class SendVerifyCodeSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        email = validated_data.get('email')

        instance = create_verification_record(email)

        send_mail(
            subject='Verify your account',
            message='This is a verify code: {}'.format(instance.verify_code),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email]
        )

        return instance

    class Meta:
        model = Account
        fields = ['email']


class SignupSerializer(serializers.ModelSerializer):
    verify_code = serializers.CharField(max_length=settings.VERIFY_CODE_LENGTH)

    def validate(self, attrs):
        email = attrs.get('email')
        verify_code = attrs.get('verify_code')

        verification = EmailVerification.objects.filter(email=email,
                                                        verify_code=verify_code,
                                                        expired_day__gte=datetime.now())

        if not len(verification):
            raise serializers.ValidationError('The verify code is incorrect')

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            account = Account.objects.create_user(email=validated_data['email'],
                                                  password=validated_data['password'],
                                                  first_name=validated_data['first_name'],
                                                  last_name=validated_data['last_name'])

            UserProfile.objects.create(account=account)

            EmailVerification.objects.filter(email=validated_data['email']).delete()

        return validated_data

    class Meta:
        model = Account
        fields = ['email', 'password', 'first_name', 'last_name', 'verify_code']


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data['user_profile'] = {
            'id': self.user.id,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'date_joined': self.user.date_joined,
            'about': self.user.user_profile.about,
            'date_of_birth': self.user.user_profile.date_of_birth,
            'image': self.user.user_profile.image
        }

        return data


class SendResetPasswordCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=256)

    def validate(self, attrs):
        try:
            Account.objects.get(email=attrs.get('email'))
            return attrs
        except:
            raise serializers.ValidationError('Your email is not existed')

    def create(self, validated_data):
        email = validated_data.get('email')

        instance = create_verification_record(email)

        send_mail(
            subject='Verify your account',
            message='This is a verify code for reset password: {}'.format(instance.verify_code),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email]
        )

        return instance


class ResetPasswordSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=256)
    new_password = serializers.CharField(max_length=256)
    confirm_password = serializers.CharField(max_length=256)

    def validate(self, attrs):
        email = attrs.get('email')
        verify_code = attrs.get('verify_code')

        verification = EmailVerification.objects.filter(email=email,
                                                        verify_code=verify_code,
                                                        expired_day__gte=datetime.now())

        if not len(verification):
            raise serializers.ValidationError('The verify code is incorrect')

        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords dont match")

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            account = Account.objects.get(email=validated_data['email'])

            account.set_password(validated_data['new_password'])

            account.save()

            EmailVerification.objects.filter(email=validated_data['email']).delete()

        return validated_data

    class Meta:
        model = EmailVerification
        fields = ['email', 'verify_code', 'new_password', 'confirm_password']


class AccountSerializer(serializers.ModelSerializer):
    about = serializers.CharField(source="user_profile.about")
    date_of_birth = serializers.CharField(source="user_profile.date_of_birth")
    image = serializers.CharField(source="user_profile.image")
    trips = serializers.SerializerMethodField(read_only=True)

    def get_trips(self, instance):
        return len(instance.trips.all())

    class Meta:
        model = Account
        fields = ['id', 'first_name', 'last_name', 'email',
                  'date_joined', 'about', 'date_of_birth', 'trips', 'image']


class AccountUploadImageSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = instance.image.url

        return representation

    def validate(self, attrs):
        data = self.context['request'].data
        key = list(data.keys())[0]

        image = data[key]
        if not image:
            raise serializers.ValidationError('image can not be none')
        elif not less_than_2mb(image):
            raise serializers.ValidationError('image must be less than 2mb')

        attrs['image'] = image
        return attrs

    def create(self, validated_data):
        instance = self.context['request'].user.user_profile
        instance.image = validated_data['image']
        instance.save()

        return instance

    class Meta:
        model = UserProfile
        fields = []


class UpdateUserProfile(serializers.ModelSerializer):
    first_name = serializers.CharField(source='account.first_name')
    last_name = serializers.CharField(source='account.last_name')
    image = serializers.CharField(max_length=256, required=True)

    def update(self, instance, validated_data):
        with transaction.atomic():
            account = instance.account
            account.first_name = validated_data['account']['first_name']
            account.last_name = validated_data['account']['last_name']

            account.save()

            instance.about = validated_data['about']
            instance.date_of_birth = validated_data['date_of_birth']
            instance.image = validated_data['image']

            instance.save()

        return instance

    class Meta:
        model = UserProfile
        fields = ['last_name', 'first_name', 'about', 'date_of_birth', 'image']
