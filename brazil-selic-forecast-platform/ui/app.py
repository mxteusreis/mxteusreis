from __future__ import annotations

import os
from datetime import date

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Brazil Selic Forecast Platform", layout="wide")

st.title("Brazil Selic Forecast Platform")
st.subheader(
    "Consuma o histórico e previsões da taxa Selic com base nos dados do Banco Central."
)

with st.sidebar:
    st.header("Filtros")
    start_date = st.date_input("Data inicial", value=date(2015, 1, 1))
    end_date = st.date_input("Data final", value=date.today())
    horizon = st.selectbox("Horizonte (dias)", [7, 30, 90, 180], index=1)
    refresh = st.button("Update")


@st.cache_data(show_spinner=False)
def fetch_series(start: date, end: date) -> pd.DataFrame:
    response = requests.get(
        f"{API_BASE_URL}/series/selic",
        params={"start": start.isoformat(), "end": end.isoformat()},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()["series"]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna()


@st.cache_data(show_spinner=False)
def fetch_forecast(horizon_days: int) -> pd.DataFrame:
    response = requests.get(
        f"{API_BASE_URL}/forecast/selic",
        params={"horizon": horizon_days},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()["forecasts"]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna()


if refresh:
    fetch_series.clear()
    fetch_forecast.clear()


try:
    series_df = fetch_series(start_date, end_date)
    forecast_df = fetch_forecast(horizon)
except requests.RequestException as exc:
    st.error(f"Erro ao consultar API: {exc}")
    st.stop()

if series_df.empty:
    st.warning("Nenhum dado disponível para o intervalo informado.")
    st.stop()

st.metric("Última Selic", f"{series_df['value'].iloc[-1]:.2f}")

history_fig = px.line(series_df, x="date", y="value", title="Histórico da Selic")
forecast_fig = px.line(
    forecast_df, x="date", y="forecast", title="Previsão da Selic"
)

combined_df = series_df.rename(columns={"value": "rate"})
forecast_series = forecast_df.rename(columns={"forecast": "rate"})
combined = pd.concat([combined_df[["date", "rate"]], forecast_series], ignore_index=True)
combined_fig = px.line(combined, x="date", y="rate", title="Histórico + Previsão")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(history_fig, use_container_width=True)
    st.download_button(
        "Download histórico CSV",
        data=series_df.to_csv(index=False),
        file_name="selic_history.csv",
        mime="text/csv",
    )
with col2:
    st.plotly_chart(forecast_fig, use_container_width=True)
    st.download_button(
        "Download forecast CSV",
        data=forecast_df.to_csv(index=False),
        file_name="selic_forecast.csv",
        mime="text/csv",
    )

st.plotly_chart(combined_fig, use_container_width=True)

st.dataframe(
    series_df.tail(10).rename(columns={"value": "selic"}),
    use_container_width=True,
)
