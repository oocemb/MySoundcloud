import os
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, parsers, views
from ..base.classes import *
from ..base.services import delete_old_file
from . import models, serializer
from ..base.permissions import IsAuthor

class GenreView(generics.ListAPIView):
    """Список жанров"""
    queryset = models.Genre.objects.all()
    serializer_class = serializer.GenreSerializer


class LicenseView(viewsets.ModelViewSet):
    """CRUD лицензий автора"""
    queryset = models.License.objects.all()
    serializer_class = serializer.LicenseSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return models.License.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)


class AlbumView(viewsets.ModelViewSet):
    """Список альбомов"""
    parser_classes = (parsers.MultiPartParser,)
    serializer_class = serializer.AlbumSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return models.Album.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        instance.delete()
        return super().perform_destroy(instance)


class PublicAlbumView(viewsets.ModelViewSet):
    """Список публичных альбомов"""
    serializer_class = serializer.AlbumSerializer

    def get_queryset(self):
        return models.Album.objects.filter(user__id=self.kwargs.get('pk'), private=False)

    
class TrackView(MixedSerializer, viewsets.ModelViewSet):
    """CRUD трэков"""
    parser_classes = (parsers.MultiPartParser,)
    serializer_class = serializer.CreateAuthorTrackSerializer
    permission_classes = [IsAuthor]
    serializer_classes_by_action = {
        'list': serializer.AuthorTrackSerializer
    }

    def get_queryset(self):
        return models.Track.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        delete_old_file(instance.file.path)
        instance.delete()
        return super().perform_destroy(instance)


class PlayListView(MixedSerializer, viewsets.ModelViewSet):
    """CRUD плэйлистов пользователя"""
    parser_classes = (parsers.MultiPartParser,)
    serializer_class = serializer.CreatePlayListSerializer
    permission_classes = [IsAuthor]
    serializer_classes_by_action = {
        'list': serializer.PlayListSerializer
    }

    def get_queryset(self):
        return models.PlayList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        instance.delete()
        return super().perform_destroy(instance)


class TrackListView(generics.ListAPIView):
    """Список всех трэков"""
    queryset = models.Track.objects.filter(album__private=False, private=False)
    serializer_class = serializer.AuthorTrackSerializer
    pagitation_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'user__display_name', 'album__name', 'genre__name']


class AuthorTrackListView(generics.ListAPIView):
    """Список всех трэков авора"""
    serializer_class = serializer.AuthorTrackSerializer
    pagitation_class = Pagination

    def get_queryset(self):
        return models.Track.objects.filter(
            user__id=self.kwargs.get('pk'), album__private=False, private=False
        )


class StreamingFileView(views.APIView):
    """Воспроизведение трэка"""
    def set_play(self):
        self.track.plays_count += 1
        self.track.save()

    def get(self, request, pk):
        self.track = get_object_or_404(models.Track, id=pk, private=False)
        if os.path.exists(self.track.file.path):
            self.set_play()
            response = HttpResponse('', content_type='audio/mpeg', status=206)
            response['X-Accel-Redirect'] = f'/mp3/{self.track.file.name}'
            return response
        else:
            return Http404


class StreamingFileAuthorView(views.APIView):
    """Воспроизведение трэка автора
    """
    permission_classes = [IsAuthor]

    def get(self, request, pk):
        self.track = get_object_or_404(models.Track, id=pk, user=request.user)
        if os.path.exists(self.track.file.path):
            self.set_play()
            response = HttpResponse('', content_type='audio/mpeg', status=206)
            response['X-Accel-Redirect'] = f'/mp3/{self.track.file.name}'
            return response
        else:
            return Http404


class DownloadTrackView(views.APIView):
    """Скачивание трэка
    """

    def set_download(self):
        self.track.dowloads += 1
        self.track.save()
    
    def get(self, request, pk):
        self.track = get_object_or_404(models.Track, id=pk)
        if os.path.exists(self.track.file.path):
            self.set_download()
            response = HttpResponse('', content_type='audio/mpeg', status=206)
            response['Content-Disposition'] = f'attachment; filename={self.track.file.name}'
            response['X-Accel-Redirect'] = f'/media/{self.track.file.name}'
            return response
        else:
            return Http404


class CommentAuthorView(viewsets.ModelViewSet):
    """CRUD коментариев автора
    """

    serializer_class = serializer.CommentAuthorSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return models.Comment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)


class CommentView(viewsets.ModelViewSet):
    """Коментарии к треку
    """
    serializer_class = serializer.CommentAuthorSerializer

    def get_queryset(self):
        return models.Comment.objects.filter(track_id=self.kwargs.get('pk'))
