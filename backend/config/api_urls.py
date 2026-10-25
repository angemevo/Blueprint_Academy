"""Routes sous le prefixe /api/.

Les routes metier (auth, learning-paths, exercises, ...) seront branchees ici
app par app a partir de la Phase 2.
"""

from django.urls import include, path

from apps.exercises.views import NodeCatalogView

from .views import HealthView

app_name = "api"

urlpatterns = [
    path("auth/", include("apps.users.urls")),
    path("users/", include("apps.users.users_urls")),
    path("learning-paths/", include("apps.learning.urls")),
    path("lessons/", include("apps.learning.lessons_urls")),
    path("progress/", include("apps.progress.urls")),
    path("exercises/", include("apps.exercises.urls")),
    path("node-catalog/", NodeCatalogView.as_view(), name="node-catalog"),
    path("health/", HealthView.as_view(), name="health"),
]
