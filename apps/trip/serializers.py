from rest_framework import serializers

from apps.account.models import Account
from apps.trip.models import Trip, Album


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'name', 'location', 'image', 'collaborators', 'album']


class NestedAccountSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='user_profile.image')

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'image']


class TripDetailSerializer(serializers.ModelSerializer):
    owner = NestedAccountSerializer()
    collaborators = NestedAccountSerializer(many=True)

    class Meta:
        model = Trip
        fields = ['id', 'name', 'location', 'image', 'owner', 'collaborators']


class AlbumSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField(read_only=True)

    def get_images(self, instance):
        print(instance.trips.all())
        images = list(map(lambda x: x.image.url if x.image else None, instance.trips.all()))
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
