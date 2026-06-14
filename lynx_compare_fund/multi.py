"""Backward-compatibility re-export.

The canonical home for multi-fund ranking is
:mod:`lynx_compare_core.multi`. This thin shim keeps the historical
``lynx_compare_fund.multi`` import path working unchanged after the
package split (the test-suite imports both the public helpers and a few
private names from here).
"""

import sys

from lynx_compare_core import multi as _canonical

sys.modules[__name__] = _canonical
