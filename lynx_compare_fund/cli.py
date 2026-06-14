"""Backward-compatibility re-export.

The canonical home for the CLI is :mod:`lynx_compare_ui.cli`. This thin
shim keeps the historical ``lynx_compare_fund.cli`` import path — used by
``lynx_compare_fund.__main__`` and the test-suite (``build_parser``) —
working unchanged after the package split.
"""

import sys

from lynx_compare_ui import cli as _canonical

sys.modules[__name__] = _canonical
