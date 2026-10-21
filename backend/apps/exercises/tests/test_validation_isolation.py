"""Isolement de l'app validation (CLAUDE.md, « Architecture backend »).

Tout import de `apps.validation` depuis `apps.exercises` doit rester LOCAL a une
fonction. L'analyse se fait avec `ast` : un import sous `if TYPE_CHECKING:` ou
dans un corps de classe est au niveau module, et refuse lui aussi.
"""

import ast
from pathlib import Path

import pytest

import apps.exercises

ISOLATED = "apps.validation"
EXERCISES_ROOT = Path(apps.exercises.__file__).resolve().parent
BACKEND_ROOT = EXERCISES_ROOT.parent.parent


def _is_isolated(name: str) -> bool:
    return name == ISOLATED or name.startswith(ISOLATED + ".")


def _imported_names(node: ast.Import | ast.ImportFrom, package: str) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if node.level:  # import relatif : remonter de (level - 1) paquets
        parts = package.split(".")
        parts = parts[: len(parts) - node.level + 1]
        base = ".".join([*parts, node.module] if node.module else parts)
    else:
        base = node.module or ""
    return [base, *(f"{base}.{alias.name}" for alias in node.names)]


def module_level_validation_imports(source: str, package: str) -> list[int]:
    """Lignes ou `apps.validation` est importe hors de toute fonction."""
    offending: list[int] = []

    def visit(node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                continue  # import local : autorise
            if isinstance(child, ast.Import | ast.ImportFrom) and any(
                map(_is_isolated, _imported_names(child, package))
            ):
                offending.append(child.lineno)
            visit(child)

    visit(ast.parse(source))
    return offending


def test_aucun_import_de_validation_au_niveau_module_dans_exercises():
    paths = sorted(EXERCISES_ROOT.rglob("*.py"))
    assert EXERCISES_ROOT / "validators" / "registry.py" in paths

    violations = []
    for path in paths:
        # Paquet du module (imports relatifs) : son dossier, `__init__.py` compris.
        package = ".".join(path.relative_to(BACKEND_ROOT).parent.parts)
        for line in module_level_validation_imports(path.read_text("utf-8"), package):
            violations.append(f"{path.relative_to(EXERCISES_ROOT)}:{line}")

    assert not violations, f"importer apps.validation dans une fonction : {violations}"


# --- L'analyseur lui-meme, pour que le test ci-dessus ne passe pas a vide.
PACKAGE = "apps.exercises.validators"


@pytest.mark.parametrize(
    ("source", "refused"),
    [
        ("import apps.validation.interfaces as interfaces", True),
        ("from apps.validation.interfaces import ValidationResult", True),
        ("from apps import validation", True),
        ("from ...validation import interfaces", True),
        ("if TYPE_CHECKING:\n    from apps.validation import interfaces", True),
        ("class Foo:\n    from apps.validation import interfaces", True),
        ("def f():\n    from apps.validation.interfaces import ValidationResult", False),
        ("class Foo:\n    def m(self):\n        import apps.validation", False),
        ("from ..enums import ExerciseType", False),
        ("import apps.validations_bis", False),
    ],
)
def test_analyseur(source, refused):
    assert bool(module_level_validation_imports(source, PACKAGE)) is refused
