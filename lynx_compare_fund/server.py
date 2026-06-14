"""Backward-compatibility re-export.

The canonical home for the Flask server is :mod:`lynx_compare_web.server`.
This thin shim keeps the ``lynx_compare_fund.server:run_server`` entry
point (declared in pyproject.toml) and the historical import path working
unchanged after the package split.
"""

import sys

from lynx_compare_web import server as _canonical

sys.modules[__name__] = _canonical
