from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def infer_frequency(dates: pd.Series) -> str:
    freq = pd.infer_freq(dates)
    return freq or "D"


def build_lag_matrix(values: Iterable[float], lags: list[int]) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.DataFrame({"value": list(values)})
    for lag in lags:
        df[f"lag_{lag}"] = df["value"].shift(lag)
    df = df.dropna()
    X = df[[f"lag_{lag}" for lag in lags]]
    y = df["value"]
    return X, y


def iterative_forecast(
    model: LinearRegression, history: list[float], horizon: int, lags: list[int]
) -> np.ndarray:
    values = history.copy()
    forecasts = []
    for _ in range(horizon):
        features = [values[-lag] for lag in lags]
        pred = model.predict([features])[0]
        forecasts.append(pred)
        values.append(pred)
    return np.array(forecasts)
