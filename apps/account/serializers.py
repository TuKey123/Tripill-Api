from django.core.mail import send_mail
from rest_framework import serializers
from django.conf import settings
from datetime import datetime, timedelta
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.enums.enums import Gender
from .models import EmailVerification, Account, UserProfile

import random


class SendVerifyCodeSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        email = validated_data.get('email')
        verify_code = random.randint(10 ** (settings.VERIFY_CODE_LENGTH - 1), 10 ** settings.VERIFY_CODE_LENGTH - 1)
        expired_day = datetime.now() + timedelta(hours=settings.VERIFY_CODE_EXPIRED_HOURS)

        (instance, _) = EmailVerification.objects.update_or_create(email=email, defaults={'verify_code': verify_code,
                                                                                          'expired_day': expired_day})

        send_mail(
            subject='Verify your account',
            message='This is a verify code: {}'.format(verify_code),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email]
        )

        return instance

    class Meta:
        model = Account
        fields = ['email']


class SignupSerializer(serializers.ModelSerializer):
    gender = serializers.IntegerField()
    verify_code = serializers.CharField(max_length=settings.VERIFY_CODE_LENGTH)

    def validate_gender(self, value):
        if value not in Gender.values:
            raise serializers.ValidationError('Gender is invalid')

        return True

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

            UserProfile.objects.create(account=account, gender=validated_data['gender'])

            EmailVerification.objects.filter(email=validated_data['email']).delete()

        return validated_data

    class Meta:
        model = Account
        fields = ['email', 'password', 'first_name', 'last_name', 'gender', 'verify_code']


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data['email'] = self.user.email
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['gender'] = self.user.user_profile.gender

        return data
