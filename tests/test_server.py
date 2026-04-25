"""REST server route tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def client():
    from lynx_compare_fund.server import build_app
    app = build_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    rv = client.get("/health")
    assert rv.status_code == 200
    assert rv.get_json()["status"] == "ok"


def test_version(client):
    rv = client.get("/version")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["name"] == "lynx-compare-fund"
    assert data["version"]


def test_compare_requires_both_tickers(client):
    rv = client.post("/compare", json={"a": "VFIAX"})
    assert rv.status_code == 400
