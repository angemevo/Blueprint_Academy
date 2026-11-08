"""Seed du parcours « Blueprint Fundamentals » : structure uniquement.

PROPOSITION A VALIDER PAR ANGE : tous les noms ci-dessous (skills, modules)
sont des propositions tirees de la section « Competences de sortie » de
CLAUDE.md. Rien n'est publie, aucune lecon n'est redigee, aucun contenu
technique Unreal n'est affirme ici.

Idempotent : `get_or_create` sur le slug. Relancer ne duplique rien et
n'ecrase jamais une modification faite ensuite dans l'admin.
"""

from django.db import transaction

from apps.learning.models import LearningPath, Module, Skill, SkillCategory
from common.enums import Difficulty

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
    created = {"skills": 0, "paths": 0, "modules": 0}

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
        _, new = Module.objects.get_or_create(
            learning_path=path,
            slug=slug,
            defaults={"title": title, "order": order, "is_published": False},
        )
        created["modules"] += new

    return created
