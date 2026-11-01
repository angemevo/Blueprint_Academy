"""Publication / depublication de contenu, avec controle d'integrite.

Utilise par les actions de l'admin. Retourne un compte rendu au lieu de lever :
l'admin affiche les messages, jamais d'erreur 500.
"""

from django.core.exceptions import ValidationError

from apps.learning.models import Module

from .integrity import ensure_publishable, skill_integrity_problems


def _problems_of(exc: ValidationError) -> list[str]:
    return list(exc.messages)


def publish(instance) -> list[str]:
    """Publie `instance`. Retourne la liste des problemes (vide = publie)."""
    if isinstance(instance, Module):
        skills = {s for lesson in instance.lessons.all() for s in lesson.skills_taught.all()}
        problems = skill_integrity_problems(sorted(skills, key=lambda s: s.name))
    else:
        problems = []
        try:
            if hasattr(instance, "skills_taught") or hasattr(instance, "modules"):
                ensure_publishable(instance)
        except ValidationError as exc:
            problems = _problems_of(exc)
    if problems:
        return [f"« {instance} » ne peut pas etre publie : {p}" for p in problems]
    instance.is_published = True
    try:
        instance.save()
    except ValidationError as exc:
        return [f"« {instance} » : {m}" for m in exc.messages]
    return []


def unpublish(instance) -> None:
    instance.is_published = False
    instance.save()
