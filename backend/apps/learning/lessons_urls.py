from django.urls import path

from . import views

urlpatterns = [
    path("<int:pk>/", views.LessonDetailView.as_view(), name="lessons-detail"),
]
