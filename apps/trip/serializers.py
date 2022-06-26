from django.db import transaction
from rest_framework import serializers

from apps.account.models import Account, UserProfile
from apps.trip.models import Trip, Album, Item, AppreciatedItem


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'name', 'location', 'image', 'collaborators', 'album']


class NestedAccountSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='user_profile.image')

    class Meta:
        model = Account
        fields = ['id', 'first_name', 'last_name', 'email', 'image']


class TripItemSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField(read_only=True)
    number_of_likes = serializers.SerializerMethodField(read_only=True)

    def get_is_liked(self, instance):
        user = self.context['request'].user

        appreciated_item = user.appreciated_items.all().filter(item=instance).first()

        return True if appreciated_item else False

    def get_number_of_likes(self, instance):
        return instance.appreciated_users.all().count()

    class Meta:
        model = Item
        fields = ['id', 'lat', 'lng', 'location', 'image', 'description',
                  'start_date', 'end_date', 'trip', 'note', 'is_shared', 'is_liked', 'number_of_likes']


class TripDetailSerializer(serializers.ModelSerializer):
    owner = NestedAccountSerializer()
    collaborators = NestedAccountSerializer(many=True)
    items = TripItemSerializer(many=True)

    class Meta:
        model = Trip
        fields = ['id', 'name', 'location', 'description', 'image', 'owner',
                  'start_date', 'end_date', 'collaborators', 'items']


class AlbumSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField(read_only=True)

    def get_images(self, instance):
        images = list(map(lambda x: x.image if x.image else None, instance.trips.all()))
        return images

    class Meta:
        model = Album
        fields = ['id', 'name', 'images']


class AlbumDetailSerializer(serializers.ModelSerializer):
    trips = TripSerializer(many=True)

    class Meta:
        model = Album
        fields = ['id', 'name', 'trips']


class UpdateAlbumItemsSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        album = validated_data.get('album', None)

        if album is None:
            instance.album = album
            instance.save()
            return instance

        return super().update(instance, validated_data)

    class Meta:
        model = Trip
        fields = ['album']


class CreateAlbumSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return Album.objects.create(name=validated_data['name'], owner_id=self.context['request'].user.id)

    class Meta:
        model = Album
        fields = ['id', 'name']


class UpdateAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['id', 'name']


class CreateTripSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = self.context['request'].user

        return Trip.objects.create(owner=user, **validated_data)

    class Meta:
        model = Trip
        fields = ['id', 'name', 'location', 'image', 'start_date', 'end_date']


class UpdateTripSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        user = self.context['request'].user

        if self.instance.owner.id != user.id:
            raise serializers.ValidationError('you dont own this trip')

        return attrs

    class Meta:
        model = Trip
        fields = ['id', 'name', 'description', 'image', 'start_date', 'end_date']


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'trip', 'lat', 'lng', 'description', 'location', 'image', 'start_date', 'end_date', 'note']


class ShareItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'is_shared']


class UsersSharedSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source='user_profile.image')
    number_of_likes = serializers.SerializerMethodField(read_only=True)

    def get_number_of_likes(self, instance):
        item = self.context.get("item")
        with transaction.atomic():
            account_item = Item.objects.filter(lat=item.lat, lng=item.lng, trip__owner_id=instance.id).first()

            return account_item.appreciated_users.all().count()

    class Meta:
        model = Account
        fields = ['id', 'image', 'first_name', 'last_name', 'email', 'number_of_likes']
