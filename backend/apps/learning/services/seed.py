"""Seed du parcours « Blueprint Fundamentals » : structure uniquement.

PROPOSITION A VALIDER PAR ANGE : tous les noms ci-dessous (skills, modules)
sont des propositions tirees de la section « Competences de sortie » de
CLAUDE.md. Rien n'est publie, aucune lecon n'est redigee, aucun contenu
technique Unreal n'est affirme ici.

Idempotent : `get_or_create` sur le slug. Relancer ne duplique rien et
n'ecrase jamais une modification faite ensuite dans l'admin.
"""

from django.db import transaction

from apps.exercises.models import Exercise
from apps.learning.models import LearningPath, Lesson, Module, Skill, SkillCategory
from common.enums import Difficulty

from . import seed_content

PATH_SLUG = "blueprint-fundamentals"

PATH = {
    "title": "Blueprint Fundamentals",
    "subtitle": "Proposition de structure, a valider",
    "difficulty": Difficulty.BEGINNER,
}

# (slug, nom, categorie)
SKILLS = [
    ("editor-basics", "Prise en main de l'editeur", SkillCategory.FUNDAMENTALS),
    ("actor-blueprint", "Creer un Actor Blueprint", SkillCategory.ACTORS),
    ("variables", "Variables", SkillCategory.VARIABLES),
    ("health-and-damage", "Systeme de vie et de degats", SkillCategory.GAMEPLAY),
    ("blueprint-interfaces", "Interfaces Blueprint", SkillCategory.OOP),
    ("widget-health-bar", "Afficher une barre de vie avec un Widget", SkillCategory.UI),
    ("compile-and-debug", "Compiler et lire les erreurs", SkillCategory.DEBUGGING),
]

# (slug, titre) dans l'ordre du parcours
MODULES = [
    ("prise-en-main-editeur", "Prise en main de l'editeur"),
    ("actor-vie-et-degats", "Un Actor avec vie et degats"),
    ("communication-interfaces", "Faire communiquer deux Blueprints"),
    ("barre-de-vie-widget", "Afficher une barre de vie"),
]


@transaction.atomic
def seed_blueprint() -> dict[str, int]:
    """Cree ce qui manque ; renvoie le nombre d'objets crees par famille."""
    created = {"skills": 0, "paths": 0, "modules": 0, "lessons": 0, "exercises": 0}

    for slug, name, category in SKILLS:
        _, new = Skill.objects.get_or_create(
            slug=slug, defaults={"name": name, "category": category}
        )
        created["skills"] += new

    path, new = LearningPath.objects.get_or_create(
        slug=PATH_SLUG,
        defaults={**PATH, "is_published": False},
    )
    created["paths"] += new

    for order, (slug, title) in enumerate(MODULES, start=1):
        module, new = Module.objects.get_or_create(
            learning_path=path,
            slug=slug,
            defaults={"title": title, "order": order, "is_published": False},
        )
        created["modules"] += new
        if slug == seed_content.MODULE_SLUG:
            _seed_first_module(module, created)

    return created


def _seed_first_module(module: Module, created: dict[str, int]) -> None:
    """Lecons et exercices proposes (non publies) du premier module."""
    lessons = {}
    for order, data in enumerate(seed_content.LESSONS, start=1):
        lesson, new = Lesson.objects.get_or_create(
            module=module,
            slug=data["slug"],
            defaults={
                "title": data["title"],
                "summary": data["summary"],
                "content": data["content"],
                "estimated_minutes": data["estimated_minutes"],
                "order": order,
                "is_published": False,
            },
        )
        if new:
            lesson.skills_taught.set(Skill.objects.filter(slug__in=data["skills"]))
        created["lessons"] += new
        lessons[data["slug"]] = lesson

    for data in seed_content.EXERCISES:
        exercise, new = Exercise.objects.get_or_create(
            slug=data["slug"],
            defaults={
                "lesson": lessons[data["lesson"]],
                "type": data["type"],
                "title": data["title"],
                "content": data["content"],
                "solution": data["solution"],
                "hints": data["hints"],
                "order": data["order"],
                "is_published": False,
            },
        )
        if new:
            exercise.skills.set(Skill.objects.filter(slug__in=data["skills"]))
        created["exercises"] += new
