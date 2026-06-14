"""Backward-compatibility re-export.

The canonical home for the public API is :mod:`lynx_compare_web.api`.
This thin shim keeps the documented ``lynx_compare_fund.api`` import path
(``compare_funds``, ``compare_reports``, ``ComparisonView``) working
unchanged after the package split.
"""

import sys

from lynx_compare_web import api as _canonical

sys.modules[__name__] = _canonical
