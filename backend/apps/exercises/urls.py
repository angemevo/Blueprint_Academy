from django.urls import path

from . import views

urlpatterns = [
    path("<int:pk>/", views.ExerciseDetailView.as_view(), name="exercises-detail"),
    path("<int:pk>/submit/", views.ExerciseSubmitView.as_view(), name="exercises-submit"),
]
