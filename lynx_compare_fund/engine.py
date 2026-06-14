"""Backward-compatibility re-export.

The canonical home for the comparison engine is
:mod:`lynx_compare_core.engine`. This thin shim keeps the historical
``lynx_compare_fund.engine`` import path — relied on by the public API,
the test-suite, and ``lynx_compare_fund.__init__``'s lazy ``__getattr__``
— working unchanged after the package split.
"""

import sys

from lynx_compare_core import engine as _canonical

sys.modules[__name__] = _canonical
