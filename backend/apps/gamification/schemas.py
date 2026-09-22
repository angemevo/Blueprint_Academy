"""Schema de la regle de deverrouillage d'un achievement.

Une regle est declarative : elle se cree depuis l'admin, sans code. Le moteur
qui l'evalue vit dans la couche service (Phase 2b / P1).
"""

from typing import Any

from common.schemas import validate_against_schema


class AchievementRuleType:
    """Types de regles reconnus par le moteur."""

    LESSONS_COMPLETED = "lessons_completed"
    EXERCISES_SOLVED = "exercises_solved"
    CHALLENGES_SOLVED = "challenges_solved"
    PERFECT_EXERCISES = "perfect_exercises"  # reussis a la premiere tentative
    SKILLS_MASTERED = "skills_mastered"
    PATH_COMPLETED = "path_completed"
    TOTAL_XP = "total_xp"
    STREAK_DAYS = "streak_days"

    ALL = [
        LESSONS_COMPLETED,
        EXERCISES_SOLVED,
        CHALLENGES_SOLVED,
        PERFECT_EXERCISES,
        SKILLS_MASTERED,
        PATH_COMPLETED,
        TOTAL_XP,
        STREAK_DAYS,
    ]


ACHIEVEMENT_RULE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["type"],
    "properties": {
        "type": {"enum": AchievementRuleType.ALL},
        # Seuil a atteindre (nombre de lecons, de jours de serie, d'XP...).
        "threshold": {"type": "integer", "minimum": 1},
        # Restriction facultative du perimetre.
        "learning_path_slug": {"type": "string"},
        "skill_slug": {"type": "string"},
        "exercise_type": {"type": "string", "minLength": 1, "maxLength": 1},
    },
    "allOf": [
        {
            "if": {"properties": {"type": {"const": AchievementRuleType.PATH_COMPLETED}}},
            "then": {"required": ["learning_path_slug"]},
            "else": {"required": ["threshold"]},
        }
    ],
    "additionalProperties": False,
}


def validate_achievement_rule(rule: Any) -> None:
    """Valide une regle. Une regle vide est refusee : elle ne se declencherait jamais."""
    validate_against_schema(rule or {}, ACHIEVEMENT_RULE_SCHEMA, label="regle")
