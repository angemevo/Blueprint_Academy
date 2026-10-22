from django.urls import path

from . import views

urlpatterns = [
    path("<int:pk>/", views.ExerciseDetailView.as_view(), name="exercises-detail"),
]
