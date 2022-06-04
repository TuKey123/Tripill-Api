# Generated by Django 4.0.4 on 2022-05-28 15:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trip', '0003_alter_trip_album_alter_trip_collaborators'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='image',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subs', to='trip.item'),
        ),
        migrations.AlterField(
            model_name='trip',
            name='album',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trips', to='trip.album'),
        ),
        migrations.AlterField(
            model_name='trip',
            name='collaborators',
            field=models.ManyToManyField(blank=True, null=True, related_name='collaborate_trips', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='trip',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='/trips'),
        ),
    ]
