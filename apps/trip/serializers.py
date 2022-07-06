from django.db import transaction
from django.db.models import F
from rest_framework import serializers
from apps.account.models import Account
from apps.trip.models import Trip, Album, Item


class TripSerializer(serializers.ModelSerializer):
    days = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    number_of_likes = serializers.SerializerMethodField(read_only=True)

    def get_is_liked(self, instance):
        user = self.context['request'].user

        appreciated_trip = user.appreciated_trips.all().filter(trip=instance).first()

        return True if appreciated_trip else False

    def get_number_of_likes(self, instance):
        return instance.appreciated_users.all().count()

    def get_days(self, instance):
        days = instance.end_date - instance.start_date
        return days.days

    class Meta:
        model = Trip
        fields = ['id', 'name', 'image', 'collaborators', 'album', 'days', 'is_liked', 'number_of_likes']


class NestedAccountSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='user_profile.image')

    class Meta:
        model = Account
        fields = ['id', 'first_name', 'last_name', 'email', 'image']


class TripItemSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField(read_only=True)
    number_of_likes = serializers.SerializerMethodField(read_only=True)
    owner_id = serializers.SerializerMethodField(read_only=True)

    def get_is_liked(self, instance):
        user = self.context['request'].user

        appreciated_item = user.appreciated_items.all().filter(item=instance).first()

        return True if appreciated_item else False

    def get_number_of_likes(self, instance):
        return instance.appreciated_users.all().count()

    def get_owner_id(self, instance):
        return instance.trip.owner.id

    class Meta:
        model = Item
        fields = ['id', 'lat', 'lng', 'location', 'image', 'description',
                  'start_date', 'end_date', 'trip', 'note', 'is_shared', 'is_liked', 'number_of_likes', 'owner_id',
                  'ordinal']


class TripItemNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'image', 'location', 'lat', 'lng', 'ordinal']


class TripDetailSerializer(serializers.ModelSerializer):
    owner = NestedAccountSerializer()
    collaborators = NestedAccountSerializer(many=True)
    items = TripItemNestedSerializer(many=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['items'].sort(key=lambda x: x['ordinal'])

        return representation

    class Meta:
        model = Trip
        fields = ['id', 'name', 'description', 'image', 'owner',
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
        fields = ['id', 'name', 'image', 'start_date', 'end_date']


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
    def validate(self, attrs):
        existed_item = Item.objects.filter(trip=attrs["trip"], lat=attrs['lat'], lng=attrs['lng']).first()
        if existed_item:
            raise serializers.ValidationError('this item has already existed')

        return super().validate(attrs)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['ordinal'] = instance.ordinal

        return representation

    def create(self, validated_data):
        trip = validated_data['trip']
        validated_data['ordinal'] = trip.items.all().count()

        return super().create(validated_data)

    class Meta:
        model = Item
        fields = ['id', 'trip', 'lat', 'lng', 'location']


class ShareItemSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        user = self.context['request'].user
        item = self.instance

        if attrs['is_shared']:
            shared_item = Item.objects.filter(lat=item.lat,
                                              lng=item.lng,
                                              is_shared=True,
                                              trip__owner_id=user.id).first()

            if shared_item:
                raise serializers.ValidationError('has another item like this has been shared')

        return super().validate(attrs)

    class Meta:
        model = Item
        fields = ['id', 'is_shared']


class UsersSharedSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source='user_profile.image')
    number_of_likes = serializers.SerializerMethodField(read_only=True)
    item_id = serializers.SerializerMethodField(read_only=True)

    def get_number_of_likes(self, instance):
        item = self.context.get("item")
        with transaction.atomic():
            account_item = Item.objects.filter(lat=item.lat, lng=item.lng, is_shared=True,
                                               trip__owner_id=instance.id).first()

            return account_item.appreciated_users.all().count()

    def get_item_id(self, instance):
        item = self.context.get("item")
        with transaction.atomic():
            account_item = Item.objects.filter(lat=item.lat, lng=item.lng, is_shared=True,
                                               trip__owner_id=instance.id).first()

            return account_item.id

    class Meta:
        model = Account
        fields = ['id', 'image', 'first_name', 'last_name', 'email', 'number_of_likes', 'item_id']


class ItemOwnerSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source='user_profile.image')

    class Meta:
        model = Account
        fields = ['id', 'image', 'first_name', 'last_name', 'email']


class ItemOrdinalSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        with transaction.atomic():
            if validated_data['ordinal'] < instance.ordinal:
                Item.objects.filter(trip=instance.trip,
                                    ordinal__gte=validated_data['ordinal'],
                                    ordinal__lt=instance.ordinal).update(ordinal=F('ordinal') + 1)

            else:
                Item.objects.filter(trip=instance.trip,
                                    ordinal__gt=instance.ordinal,
                                    ordinal__lte=validated_data['ordinal']).update(ordinal=F('ordinal') - 1)

            instance.ordinal = validated_data['ordinal']
            instance.save()

            return instance

    class Meta:
        model = Item
        fields = ['id', 'ordinal']


class UpdateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'lat', 'lng', 'location', 'image', 'description',
                  'start_date', 'end_date', 'trip', 'note', ]


class ItemsSharedSerializer(serializers.ModelSerializer):
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
        fields = ['id', 'lat', 'lng', 'location', 'image', 'is_liked', 'number_of_likes']
