"""CLI argument parsing tests."""

from __future__ import annotations

import pytest

from lynx_compare_fund.cli import build_parser


def test_help_mentions_fund():
    parser = build_parser()
    txt = parser.format_help().lower()
    assert "fund" in txt


def test_parses_two_tickers():
    args = build_parser().parse_args(["-p", "VFIAX", "FXAIX"])
    assert args.run_mode == "production"
    assert args.ticker_a == "VFIAX"
    assert args.ticker_b == "FXAIX"


def test_testing_mode():
    args = build_parser().parse_args(["-t", "VFIAX", "FXAIX"])
    assert args.run_mode == "testing"


def test_ui_flags_exclusive():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["-p", "-i", "-tui"])


def test_json_flag():
    args = build_parser().parse_args(["-p", "VFIAX", "FXAIX", "--json"])
    assert args.json
