from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class SGSClient:
    base_url: str = "https://api.bcb.gov.br/dados/serie"

    def fetch_series(
        self, series_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> list[dict]:
        url = f"{self.base_url}/bcdata.sgs.{series_id}/dados"
        params = {"formato": "json"}
        if start_date:
            params["dataInicial"] = start_date
        if end_date:
            params["dataFinal"] = end_date
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
