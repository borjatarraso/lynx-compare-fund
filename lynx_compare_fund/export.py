"""Backward-compatibility re-export.

The canonical home for the export helpers is
:mod:`lynx_compare_web.export`. This thin shim keeps the historical
``lynx_compare_fund.export`` import path (``to_json``, ``to_text``,
``to_html``, ``save``) working unchanged after the package split.
"""

import sys

from lynx_compare_web import export as _canonical

sys.modules[__name__] = _canonical
