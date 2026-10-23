from django.urls import path

from apps.progress import views as progress_views

from . import views

urlpatterns = [
    path("<int:pk>/", views.LessonDetailView.as_view(), name="lessons-detail"),
    path("<int:pk>/start/", progress_views.LessonStartView.as_view(), name="lessons-start"),
    path(
        "<int:pk>/complete/",
        progress_views.LessonCompleteView.as_view(),
        name="lessons-complete",
    ),
]
