from django.db import transaction
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.account.models import Account
from apps.trip.models import Trip, Album, Item, AppreciatedItem
from apps.trip.serializers import (TripSerializer, TripDetailSerializer, AlbumSerializer, AlbumDetailSerializer,
                                   UpdateAlbumItemsSerializer, CreateAlbumSerializer, UpdateAlbumSerializer,
                                   CreateTripSerializer, UpdateTripSerializer, ItemSerializer, ShareItemSerializer,
                                   UsersSharedSerializer, TripItemSerializer, ItemOwnerSerializer,
                                   ItemOrdinalSerializer)
from django.db.models import Q, F


class AlbumView(viewsets.GenericViewSet,
                mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                mixins.CreateModelMixin,
                mixins.UpdateModelMixin,
                mixins.DestroyModelMixin):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AlbumDetailSerializer
        elif self.action == 'create':
            return CreateAlbumSerializer
        elif self.action == 'update':
            return UpdateAlbumSerializer
        return AlbumSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(owner=self.request.user)
        serializer = self.get_serializer(queryset, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()

        if user.id != instance.owner.id:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return super().destroy(request, args, kwargs)

    @action(detail=False, url_path="users/(?P<user_id>[0-9]+)", methods=['Get'])
    def user_albums(self, request, user_id=None):
        queryset = self.get_queryset().filter(owner__id=user_id)
        serializer = self.get_serializer(queryset, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_path="trips/(?P<trip_id>[0-9]+)", methods=['Delete'])
    def delete_trip(self, request, pk=None, trip_id=None):
        user = request.user
        instance = self.get_object()

        trip = instance.trips.all().filter(id=trip_id).first()

        if user.id != instance.owner.id or not trip:
            return Response(status=status.HTTP_404_NOT_FOUND)

        trip.album = None
        trip.save()

        return Response(status=status.HTTP_200_OK)


class TripView(viewsets.GenericViewSet,
               mixins.ListModelMixin,
               mixins.RetrieveModelMixin,
               mixins.CreateModelMixin,
               mixins.UpdateModelMixin,
               mixins.DestroyModelMixin):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TripDetailSerializer
        elif self.action == 'update_album':
            return UpdateAlbumItemsSerializer
        elif self.action == 'create':
            return CreateTripSerializer
        elif self.action == 'update':
            return UpdateTripSerializer
        return TripSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(owner=self.request.user).order_by('id').reverse()
        serializer = self.get_serializer(queryset, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path="users/(?P<user_id>[0-9]+)", methods=['Get'])
    def user_trips(self, request, user_id=None):
        queryset = self.get_queryset().filter(owner__id=user_id)
        serializer = self.get_serializer(queryset, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_path='update-album', methods=['Put'])
    def update_album(self, request, pk=None):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_path="items/(?P<item_id>[0-9]+)", methods=['Delete'])
    def remove_item(self, request, pk=None, item_id=None):
        user = request.user

        instance = self.get_object()

        if instance.owner.id != user.id:
            return Response(status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            item = instance.items.all().filter(id=item_id).first()

            if not item:
                return Response(status=status.HTTP_404_NOT_FOUND)

            Item.objects.filter(trip=instance,
                                ordinal__gt=item.ordinal).update(ordinal=F('ordinal') - 1)

            item.delete()

        return Response(status=status.HTTP_200_OK)


class ItemViewSet(viewsets.GenericViewSet,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin):
    queryset = Item.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSerializer

    def get_serializer_class(self):
        if self.action == 'share_item':
            return ShareItemSerializer
        elif self.action == 'users_shared':
            return UsersSharedSerializer
        elif self.action == 'retrieve':
            return TripItemSerializer
        elif self.action == 'user':
            return ItemOwnerSerializer
        elif self.action == 'update_ordinal':
            return ItemOrdinalSerializer
        elif self.action == 'like':
            return None
        return ItemSerializer

    def retrieve(self, request, *args, **kwargs):
        if not self.get_object().is_shared:
            return Response(data="this item has not been shared", status=status.HTTP_400_BAD_REQUEST)
        return super().retrieve(request, args, kwargs)

    @action(detail=True, url_path='like', methods=['Put'])
    def like(self, request, pk=None):
        instance = self.get_object()
        user = request.user

        appreciated_item = user.appreciated_items.all().filter(item=instance).first()
        if appreciated_item:
            appreciated_item.delete()
        else:
            AppreciatedItem.objects.create(user=user, item=instance)

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, url_path='share', methods=['Put'])
    def share_item(self, request, pk=None):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, url_path='users_shared', methods=['get'])
    def users_shared(self, request, pk=None):
        user = request.user
        instance = self.get_object()

        queryset = Account.objects.filter(~Q(id=user.id),
                                          trips__items__lat=instance.lat,
                                          trips__items__lng=instance.lng,
                                          trips__items__is_shared=True)

        serializer = self.get_serializer(queryset, many=True, context={'item': instance})

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_path='user', methods=['get'])
    def user(self, request, pk=None):
        instance = self.get_object()
        owner = instance.trip.owner

        serializer = self.get_serializer(owner)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_path='update_ordinal', methods=['put'])
    def update_ordinal(self, request, pk=None):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)
