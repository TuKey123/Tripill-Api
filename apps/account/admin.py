from django.contrib import admin
from apps.account.models import UserProfile, Account, EmailVerification

admin.site.register(Account)
admin.site.register(UserProfile)
admin.site.register(EmailVerification)
