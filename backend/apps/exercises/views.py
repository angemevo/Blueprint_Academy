from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ExerciseDetailSerializer, SubmissionSerializer
from .services import catalog, submission


class ExerciseDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExerciseDetailSerializer

    def get_queryset(self):
        return catalog.exercises_queryset(self.request.user)


class ExerciseSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        exercise = get_object_or_404(catalog.exercises_queryset(request.user), pk=pk)
        serializer = SubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            attempt, result = submission.submit_exercise(
                request.user,
                exercise,
                data["submission"],
                duration_seconds=data.get("duration_seconds"),
                hints_used=data["hints_used"],
            )
        except submission.MaxAttemptsReached as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except submission.ValidatorNotAvailable as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_501_NOT_IMPLEMENTED)
        return Response(submission.serialize_result(attempt, result))
