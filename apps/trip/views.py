from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.trip.models import Trip, Album
from apps.trip.serializers import (TripSerializer, TripDetailSerializer, AlbumSerializer, AlbumDetailSerializer,
                                   UpdateAlbumItemsSerializer, CreateAlbumSerializer)


class AlbumView(viewsets.GenericViewSet,
                mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                mixins.CreateModelMixin):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AlbumDetailSerializer
        elif self.action == 'create':
            return CreateAlbumSerializer
        return AlbumSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(owner=self.request.user)
        serializer = self.get_serializer(queryset, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path="users/(?P<user_id>[0-9]+)", methods=['Get'])
    def user_albums(self, request, user_id=None):
        queryset = self.get_queryset().filter(owner__id=user_id)
        serializer = self.get_serializer(queryset, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class TripView(viewsets.GenericViewSet,
               mixins.ListModelMixin,
               mixins.RetrieveModelMixin):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TripDetailSerializer
        elif self.action == 'update_album':
            return UpdateAlbumItemsSerializer
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
