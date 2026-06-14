"""Backward-compatibility re-export.

The canonical home for branding/about metadata is
:mod:`lynx_compare_ui.about`. This thin shim keeps the historical
``lynx_compare_fund.about`` import path (used by the test-suite) working
unchanged after the package split.
"""

import sys

from lynx_compare_ui import about as _canonical

sys.modules[__name__] = _canonical
