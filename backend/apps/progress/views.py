"""Vues de progression : valident, delèguent aux services."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.learning.services import catalog
from apps.progress.services import dashboard
from apps.progress.services import lessons as svc


class _LessonActionView(APIView):
    permission_classes = [IsAuthenticated]
    action = None

    def post(self, request, pk):
        lesson = get_object_or_404(catalog.lessons_queryset(request.user), pk=pk)
        try:
            lp = getattr(svc, self.action)(request.user, lesson)
        except svc.LessonLocked as exc:
            return Response(
                {
                    "detail": "Leçon verrouillée.",
                    "locked": True,
                    "missing_skills": [
                        {"id": s.id, "name": s.name} for s in exc.missing
                    ],
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(
            {
                "lesson": lesson.id,
                "status": lp.status,
                "started_at": lp.started_at,
                "completed_at": lp.completed_at,
            }
        )


class LessonStartView(_LessonActionView):
    action = "start_lesson"


class LessonCompleteView(_LessonActionView):
    action = "complete_lesson"


class ProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        paths = catalog.paths_queryset(request.user)
        return Response({"results": svc.progress_overview(request.user, paths)})


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(dashboard.build_dashboard(request.user))
