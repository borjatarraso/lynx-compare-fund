"""Flask REST API for lynx-compare-fund."""

from __future__ import annotations

import dataclasses

from lynx_compare_fund import __version__


def build_app():
    from flask import Flask, jsonify, request

    from lynx_compare_fund.api import compare_funds
    from lynx_compare_fund.engine import ComparisonResult
    from lynx_fund.core.storage import set_mode
    from lynx_fund.core.ticker import NotAFundError

    app = Flask("lynx-compare-fund")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "version": __version__})

    @app.get("/version")
    def version():
        return jsonify({"name": "lynx-compare-fund", "version": __version__})

    @app.post("/compare")
    def compare_route():
        payload = request.get_json(silent=True) or {}
        a = (payload.get("a") or "").strip()
        b = (payload.get("b") or "").strip()
        mode = payload.get("mode", "production")
        refresh = bool(payload.get("refresh"))

        if not a or not b:
            return jsonify({"error": "Both 'a' and 'b' tickers are required"}), 400

        try:
            set_mode(mode)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        try:
            result = compare_funds(a, b, refresh=refresh)
        except NotAFundError as exc:
            return jsonify({"error": str(exc)}), 422
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify(_result_to_dict(result))

    return app


def _result_to_dict(result) -> dict:
    d = dataclasses.asdict(result)
    # Replace SectionResult.metrics enum-style winner strings which are already strings.
    return d


def run_server(host: str = "127.0.0.1", port: int = 5054, debug: bool = False) -> int:
    app = build_app()
    app.run(host=host, port=port, debug=debug)
    return 0


if __name__ == "__main__":
    run_server()
