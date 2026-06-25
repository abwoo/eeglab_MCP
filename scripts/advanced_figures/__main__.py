"""CLI entry point for the default advanced figure gallery."""

from __future__ import annotations

from . import ALL_MODULES
from .catalog import render_index_doc


def main() -> None:
    print(render_index_doc(ALL_MODULES))


if __name__ == "__main__":
    main()
