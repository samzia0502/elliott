import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from scipy.signal import find_peaks
import openai
import pandas as pd

st.set_page_config(page_title="Elliott Wave AI Dashboard", layout="wide")
st.title("📈 Elliott Wave AI Dashboard (1H Stocks)")

ticker = st.text_input("Enter Stock Ticker (e.g. AAPL)", "AAPL")
api_key = st.text_input("Enter OpenAI API Key (for wave summary)", type="password")

if st.button("Run Analysis"):
    with st.spinner("Fetching data and analyzing..."):
        data = yf.download(ticker, interval="1h", period="7d")
        data.dropna(inplace=True)

                # Detect local peaks and troughs
        peaks, _ = find_peaks(data["Close"], distance=5)
        troughs, _ = find_peaks(-data["Close"], distance=5)

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Candles"
        ))

        fig.add_trace(go.Scatter(
            x=data.index[peaks],
            y=data["Close"].iloc[peaks],
            mode="markers+text",
            name="Peaks",
            marker=dict(color="red", size=10),
            text=["1", "3", "5"],
            textposition="top center"
        ))

        fig.add_trace(go.Scatter(
            x=data.index[troughs],
            y=data["Close"].iloc[troughs],
            mode="markers+text",
            name="Troughs",
            marker=dict(color="green", size=10),
            text=["2", "4"],
            textposition="bottom center"
        ))

        st.plotly_chart(fig, use_container_width=True)
