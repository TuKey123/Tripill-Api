# Generated by Django 4.0.4 on 2022-05-28 06:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='albums', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('location', models.CharField(max_length=256)),
                ('image', models.ImageField(blank=True, upload_to='', verbose_name='/trips')),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trips', to='trip.album')),
                ('collaborators', models.ManyToManyField(related_name='collaborate_trips', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trips', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.CharField(max_length=256)),
                ('lng', models.CharField(max_length=256)),
                ('address', models.CharField(max_length=256)),
                ('is_single', models.BooleanField(default=True)),
                ('image', models.CharField(max_length=256)),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='trip.trip')),
            ],
        ),
    ]
