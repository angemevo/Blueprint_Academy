"""Routes sous le prefixe /api/.

Les routes metier (auth, learning-paths, exercises, ...) seront branchees ici
app par app a partir de la Phase 2.
"""

from django.urls import path

from .views import HealthView

app_name = "api"

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
]
