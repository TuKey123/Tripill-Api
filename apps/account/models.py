from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.enums.enums import Gender


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class Account(AbstractUser):
    username = None

    email = models.EmailField(max_length=256, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, null=True, related_name='user_profile')
    gender = models.IntegerField(choices=Gender.choices, default=Gender.FEMALE)
    image = models.ImageField(upload_to='users/', blank=True)

    def __str__(self):
        return self.account.email


class EmailVerification(models.Model):
    email = models.EmailField(max_length=256, unique=True)
    verify_code = models.CharField(max_length=settings.VERIFY_CODE_LENGTH)
    expired_day = models.DateTimeField()
