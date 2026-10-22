from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .serializers import ExerciseDetailSerializer
from .services import catalog


class ExerciseDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExerciseDetailSerializer

    def get_queryset(self):
        return catalog.exercises_queryset(self.request.user)
