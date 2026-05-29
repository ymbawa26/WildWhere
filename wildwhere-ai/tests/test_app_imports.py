import ast
import importlib
from pathlib import Path


def test_streamlit_support_modules_import():
    for module in [
        "app.components.cards",
        "app.components.charts",
        "app.components.filters",
        "app.components.layout",
    ]:
        importlib.import_module(module)


def test_streamlit_pages_have_no_hardcoded_secrets():
    for path in list(Path("app").rglob("*.py")) + list(Path("ai").rglob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                value = node.value.lower()
                assert "sk-" not in value
                assert "api_key=" not in value
