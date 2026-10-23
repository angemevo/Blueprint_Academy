from django.apps import AppConfig


class ExercisesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.exercises"
    label = "exercises"
    verbose_name = "Exercices"

    def ready(self) -> None:
        from .validators import load_validators

        load_validators()
