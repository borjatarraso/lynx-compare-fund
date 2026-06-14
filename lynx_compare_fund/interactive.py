"""Backward-compatibility re-export.

The canonical home for the interactive REPL is
:mod:`lynx_compare_ui.interactive`. This thin shim keeps the historical
``lynx_compare_fund.interactive`` import path working unchanged after the
package split.
"""

import sys

from lynx_compare_ui import interactive as _canonical

sys.modules[__name__] = _canonical
