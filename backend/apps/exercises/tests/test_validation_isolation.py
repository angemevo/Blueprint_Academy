"""Isolement de l'app validation (CLAUDE.md, « Architecture backend »).

Tout import de `apps.validation` depuis `apps.exercises` doit rester LOCAL a une
fonction : `apps.exercises` est charge avec les modeles, et un import au niveau
module creerait un couplage au chargement (voire un cycle) avec une app isolee.

On analyse le source avec `ast` plutot que d'importer les modules : un import
place sous `if TYPE_CHECKING:` ou dans le corps d'une classe s'execute (ou
s'ecrit) au niveau module, et doit etre refuse lui aussi.
"""

import ast
from pathlib import Path

import pytest

import apps.exercises

ISOLATED_PACKAGE = "apps.validation"
EXERCISES_ROOT = Path(apps.exercises.__file__).resolve().parent


def _module_package(path: Path) -> str:
    """Paquet du module, pour resoudre les imports relatifs."""
    relative = path.relative_to(EXERCISES_ROOT.parent.parent).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    else:
        parts = parts[:-1]
    return ".".join(parts)


def _resolve(node: ast.ImportFrom, package: str) -> str:
    if node.level == 0:
        return node.module or ""
    base = package.split(".")
    base = base[: len(base) - (node.level - 1)]
    return ".".join([*base, node.module] if node.module else base)


def _targets_isolated(name: str) -> bool:
    return name == ISOLATED_PACKAGE or name.startswith(ISOLATED_PACKAGE + ".")


def module_level_validation_imports(source: str, package: str) -> list[int]:
    """Lignes ou `apps.validation` est importe hors de toute fonction."""
    offending: list[int] = []

    def visit(node: ast.AST, inside_function: bool) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda):
                visit(child, True)
                continue
            if not inside_function:
                if isinstance(child, ast.Import) and any(
                    _targets_isolated(alias.name) for alias in child.names
                ):
                    offending.append(child.lineno)
                elif isinstance(child, ast.ImportFrom):
                    resolved = _resolve(child, package)
                    names = [f"{resolved}.{alias.name}" for alias in child.names]
                    if _targets_isolated(resolved) or any(map(_targets_isolated, names)):
                        offending.append(child.lineno)
            visit(child, inside_function)

    visit(ast.parse(source), False)
    return offending


def test_aucun_import_de_validation_au_niveau_module_dans_exercises():
    violations = []
    for path in sorted(EXERCISES_ROOT.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        for line in module_level_validation_imports(source, _module_package(path)):
            violations.append(f"{path.relative_to(EXERCISES_ROOT)}:{line}")

    assert not violations, (
        "apps.validation doit etre importe localement a une fonction : " f"{violations}"
    )


def test_le_parcours_couvre_bien_le_registre():
    scanned = {path.relative_to(EXERCISES_ROOT).as_posix() for path in EXERCISES_ROOT.rglob("*.py")}

    assert "validators/registry.py" in scanned


# --- L'analyseur lui-meme : sans ces cas, le test ci-dessus pourrait passer a vide.

PACKAGE = "apps.exercises.validators"


@pytest.mark.parametrize(
    "source",
    [
        "import apps.validation",
        "import apps.validation.interfaces as interfaces",
        "from apps.validation import interfaces",
        "from apps.validation.interfaces import ValidationResult",
        "from apps import validation",
        "from ...validation import interfaces",
        "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from apps.validation import interfaces",
        "class Foo:\n    from apps.validation import interfaces",
        "try:\n    import apps.validation\nexcept ImportError:\n    pass",
    ],
)
def test_analyseur_detecte_les_imports_au_niveau_module(source):
    assert module_level_validation_imports(source, PACKAGE)


@pytest.mark.parametrize(
    "source",
    [
        "def f():\n    from apps.validation.interfaces import ValidationResult",
        "async def f():\n    import apps.validation",
        "class Foo:\n    def m(self):\n        from apps.validation import interfaces",
        "from apps.exercises.enums import ExerciseType",
        "from ..enums import ExerciseType",
        "import apps.validations_bis",
    ],
)
def test_analyseur_accepte_les_imports_locaux_et_les_autres_modules(source):
    assert module_level_validation_imports(source, PACKAGE) == []
