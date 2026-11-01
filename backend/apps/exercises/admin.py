"""Admin de l'app exercises.

La validation (schema + coherence) vit dans `Exercise.clean`, qui appelle
`validate_exercise_payload` : les erreurs sont rangees sous `content` ou
`solution` par le formulaire.
"""

from django.contrib import admin

from common.admin import ContentAdmin

from .models import Exercise


@admin.register(Exercise)
class ExerciseAdmin(ContentAdmin):
    list_display = ("title", "type", "lesson", "difficulty", "order", "is_published")
    list_filter = ("is_published", "type", "difficulty", "is_practice")
    list_editable = ("order",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("skills", "required_skills")
    raw_id_fields = ("lesson",)
