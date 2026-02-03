from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from api.main import app


def create_fixture_files(base_dir: Path) -> None:
    gold_dir = base_dir / "data" / "gold"
    artifacts_dir = base_dir / "artifacts"
    gold_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {"date": ["2024-01-01", "2024-01-02"], "value": [11.75, 11.75]}
    ).to_csv(gold_dir / "selic_dataset.csv", index=False)
    pd.DataFrame(
        {"date": ["2024-01-03", "2024-01-04"], "forecast": [11.75, 11.75]}
    ).to_csv(artifacts_dir / "forecast.csv", index=False)


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_series_endpoint(monkeypatch, tmp_path: Path) -> None:
    create_fixture_files(tmp_path)
    monkeypatch.setenv("SELIC_PROJECT_ROOT", str(tmp_path))
    client = TestClient(app)
    response = client.get("/series/selic")
    assert response.status_code == 200
    assert len(response.json()["series"]) == 2


def test_forecast_endpoint(monkeypatch, tmp_path: Path) -> None:
    create_fixture_files(tmp_path)
    monkeypatch.setenv("SELIC_PROJECT_ROOT", str(tmp_path))
    client = TestClient(app)
    response = client.get("/forecast/selic?horizon=1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["horizon"] == 1
    assert len(payload["forecasts"]) == 1
