from django.db import models


class Gender(models.IntegerChoices):
    FEMALE = 1
    MALE = 2
    OTHER = 3
