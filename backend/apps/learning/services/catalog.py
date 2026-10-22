"""Requetes de lecture du catalogue, filtrees selon le role du demandeur.

Un visiteur ou un etudiant ne voit que le contenu publie ; Instructor et
Admin voient tout (relecture avant publication).
"""

from django.db.models import Prefetch

from apps.learning.models import LearningPath, Lesson, Module
from apps.users.models import Role


def can_see_unpublished(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and user.role in (Role.INSTRUCTOR, Role.ADMIN)
    )


def paths_queryset(user, with_modules: bool = False):
    """Parcours visibles ; avec `with_modules`, modules et titres de lecons visibles."""
    staff = can_see_unpublished(user)
    if not with_modules:
        qs = LearningPath.objects.all()
        if not staff:
            qs = qs.filter(is_published=True)
        return qs.order_by("order", "title")
    modules = Module.objects.all()
    lessons = Lesson.objects.only(
        "id", "module_id", "title", "slug", "summary", "order",
        "estimated_minutes", "is_published",
    )
    if not staff:
        modules = modules.filter(is_published=True)
        lessons = lessons.filter(is_published=True)
    modules = modules.prefetch_related(
        Prefetch("lessons", queryset=lessons.order_by("order", "title"))
    ).order_by("order", "title")
    qs = LearningPath.objects.prefetch_related(Prefetch("modules", queryset=modules))
    if not staff:
        qs = qs.filter(is_published=True)
    return qs.order_by("order", "title")


def lessons_queryset(user):
    """Lecons visibles ; non publiee si son module ou son parcours ne l'est pas."""
    qs = Lesson.objects.select_related("module").prefetch_related(
        "skills_taught", "required_skills"
    )
    if not can_see_unpublished(user):
        qs = qs.filter(
            is_published=True,
            module__is_published=True,
            module__learning_path__is_published=True,
        )
    return qs
