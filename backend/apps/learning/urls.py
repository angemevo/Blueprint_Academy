from django.urls import path

from . import views

urlpatterns = [
    path("", views.LearningPathListView.as_view(), name="learning-paths-list"),
    path("<slug:slug>/", views.LearningPathDetailView.as_view(), name="learning-paths-detail"),
]
