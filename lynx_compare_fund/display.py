"""Backward-compatibility re-export.

The canonical home for the Rich renderer is :mod:`lynx_compare_ui.display`.
This thin shim keeps the historical ``lynx_compare_fund.display`` import
path (used by the test-suite) working unchanged after the package split.
"""

import sys

from lynx_compare_ui import display as _canonical

sys.modules[__name__] = _canonical
