from __future__ import annotations

import pathlib
from functools import lru_cache

import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

# Path to the dataset – assumes the CSV lives under a local `data/` directory
DATA_PATH = pathlib.Path(__file__).parent / "data" / "supermarket_sales.csv"

st.set_page_config(
    page_title="Supermarket Dashboard",
    layout="wide",
    page_icon="📊",
)

# -----------------------------------------------------------------------------
# Data loading & preprocessing
# -----------------------------------------------------------------------------


@lru_cache(maxsize=1)
def load_data(path: pathlib.Path) -> pd.DataFrame:
    """Load and clean the supermarket sales dataset.

    The dataset is expected to use semicolon separators and commas as decimal
    separators (European format). Dates are parsed with *day first* notation
    based on the original Kaggle file.

    Args:
        path: Location of the ``supermarket_sales.csv`` file.

    Returns:
        A tidy :class:`pandas.DataFrame` with additional ``Month`` column.
    """
    df = pd.read_csv(path, sep=";", decimal=",")
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    df = df.sort_values("Date")

    # Create a YYYY-MM column for easy monthly filtering (Period dtype → string)
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    return df


# -----------------------------------------------------------------------------
# Sidebar helpers
# -----------------------------------------------------------------------------


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render Streamlit sidebar widgets and return the filtered DataFrame."""
    st.sidebar.header("🔎 Filtros")

    # Month selector
    month = st.sidebar.selectbox("Mês", options=df["Month"].unique())

    return df[df["Month"] == month]


# -----------------------------------------------------------------------------
# Plotting helpers – each returns a Plotly figure
# -----------------------------------------------------------------------------


def plot_revenue_by_day(df: pd.DataFrame):
    fig = px.bar(
        df,
        x="Date",
        y="Total",
        color="City",
        title="📅 Faturamento por dia",
        labels={"Total": "Faturamento", "Date": "Data"},
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_revenue_by_product(df: pd.DataFrame):
    df_prod = df.groupby(["Product line", "City"], as_index=False)["Total"].sum()
    fig = px.bar(
        df_prod,
        x="Total",
        y="Product line",
        color="City",
        orientation="h",
        title="🛍️ Faturamento por linha de produto",
        labels={"Total": "Faturamento", "Product line": "Linha de Produto"},
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_revenue_by_city(df: pd.DataFrame):
    city_total = df.groupby("City", as_index=False)["Total"].sum()
    fig = px.bar(
        city_total,
        x="City",
        y="Total",
        title="🏢 Faturamento por filial",
        labels={"Total": "Faturamento", "City": "Filial"},
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_revenue_by_payment(df: pd.DataFrame):
    fig = px.pie(
        df,
        values="Total",
        names="Payment",
        title="💳 Faturamento por forma de pagamento",
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_rating_by_city(df: pd.DataFrame):
    city_rating = df.groupby("City", as_index=False)["Rating"].mean()
    fig = px.bar(
        city_rating,
        x="City",
        y="Rating",
        title="⭐ Avaliação média por filial",
        labels={"Rating": "Avaliação Média", "City": "Filial"},
    )
    st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------------------------------
# Main app
# -----------------------------------------------------------------------------


def main() -> None:
    """Run the Streamlit dashboard."""
    st.title("📊 Supermarket Sales Dashboard")

    df = load_data(DATA_PATH)
    df_filtered = sidebar_filters(df)

    # ----- Layout ------------------------------------------------------------
    col1, col2 = st.columns(2)
    col3, col4, col5 = st.columns(3)

    with col1:
        plot_revenue_by_day(df_filtered)
    with col2:
        plot_revenue_by_product(df_filtered)
    with col3:
        plot_revenue_by_city(df_filtered)
    with col4:
        plot_revenue_by_payment(df_filtered)
    with col5:
        plot_rating_by_city(df_filtered)

    st.caption("Dados de exemplo: Supermarket Sales (© 2021 Kaggle)")


if __name__ == "__main__":
    main()
