# PYTHON_ARGCOMPLETE_OK
"""Entry point for lynx-compare-fund."""

from __future__ import annotations

import sys

from lynx_compare_fund.cli import run_cli


def main() -> int:
    rc = run_cli()
    return int(rc) if rc is not None else 0


if __name__ == "__main__":
    sys.exit(main())
