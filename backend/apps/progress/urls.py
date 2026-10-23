from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProgressView.as_view(), name="progress"),
    path("dashboard/", views.DashboardView.as_view(), name="progress-dashboard"),
]
