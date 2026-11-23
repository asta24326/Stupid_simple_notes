# importlib: standard library, import a module by its name written as a string
import importlib

import pytest

MODULES_WITH_THE_REAL_DATABASE = [
    "app.repositories.db.notes",
    "app.repositories.db.unit_of_work",
    "app.handlers.notes",
    "app.handlers.errors",
]


@pytest.mark.parametrize("module_name", MODULES_WITH_THE_REAL_DATABASE)
def test_module_can_be_imported(module_name):
    """Modules that no other test imports must at least load without errors."""
    importlib.import_module(module_name)
