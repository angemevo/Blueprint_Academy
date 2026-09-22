"""Schema du contenu d'une lecon.

Le contenu est une liste de blocs types : le frontend sait rendre chaque type,
l'auteur compose depuis l'admin sans toucher au code. La grammaire des blocs
est mutualisee avec les briefs de projets dans `common.content_blocks`.
"""

from typing import Any

from common.content_blocks import (
    BLOCK_TYPES,
    CALLOUT_VARIANTS,
    CONTENT_BLOCKS_SCHEMA,
    validate_content_blocks,
)

__all__ = [
    "BLOCK_TYPES",
    "CALLOUT_VARIANTS",
    "LESSON_CONTENT_SCHEMA",
    "validate_lesson_content",
]

LESSON_CONTENT_SCHEMA: dict[str, Any] = CONTENT_BLOCKS_SCHEMA


def validate_lesson_content(content: Any) -> None:
    """Valide le contenu d'une lecon."""
    validate_content_blocks(content, label="contenu")
