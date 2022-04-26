import tomli
from ace import __version__


def test_version():
    with open("pyproject.toml", "rb") as f:
        assert __version__ == tomli.load(f)["tool"]["poetry"]["version"]
