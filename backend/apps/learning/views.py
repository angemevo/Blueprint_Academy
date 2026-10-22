"""Vues de lecture du catalogue : valident, serialisent, deleguent au service."""

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import (
    LearningPathDetailSerializer,
    LearningPathListSerializer,
    LessonDetailSerializer,
)
from .services import catalog


class LearningPathListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = LearningPathListSerializer

    def get_queryset(self):
        return catalog.paths_queryset(self.request.user)


class LearningPathDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = LearningPathDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return catalog.paths_queryset(self.request.user, with_modules=True)


class LessonDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonDetailSerializer

    def get_queryset(self):
        return catalog.lessons_queryset(self.request.user)
