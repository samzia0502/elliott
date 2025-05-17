import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from scipy.signal import find_peaks
import openai
import pandas as pd

st.set_page_config(page_title="Elliott Wave AI Dashboard", layout="wide")
st.title("📈 Elliott Wave AI Dashboard (1H Stocks)")

# User input
ticker = st.text_input("Enter Stock Ticker (e.g. AAPL)", "AAPL")
api_key = st.text_input("Enter OpenAI API Key (for wave summary)", type="password")

if st.button("Run Analysis"):
    with st.spinner("Fetching data and analyzing..."):
        # Download historical 1-hour stock data
        data = yf.download(ticker, interval="1h", period="7d")
        if data.empty:
            st.error("⚠️ No data returned. Check the ticker symbol or your internet connection.")
            st.stop()

        close_prices = data["Close"].values

     # Ensure Close is a clean 1D array with no NaNs
close_series = data["Close"].dropna()

if close_series.empty:
    st.error("No valid price data (only NaNs). Try a different stock or time window.")
    st.stop()

close_prices = close_series.to_numpy().flatten()

# Detect local peaks and troughs
peaks, _ = find_peaks(close_prices, distance=5)
troughs, _ = find_peaks(-close_prices, distance=5)


        # Plot the candlestick chart
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Candlesticks"
        ))

        # Plot peaks (waves 1, 3, 5 as placeholders)
        fig.add_trace(go.Scatter(
            x=data.index[peaks],
            y=data["Close"].iloc[peaks],
            mode="markers+text",
            name="Peaks",
            marker=dict(color="red", size=10),
            text=["1", "3", "5"] + [""] * (len(peaks) - 3),
            textposition="top center"
        ))

        # Plot troughs (waves 2 and 4 as placeholders)
        fig.add_trace(go.Scatter(
            x=data.index[troughs],
            y=data["Close"].iloc[troughs],
            mode="markers+text",
            name="Troughs",
            marker=dict(color="green", size=10),
            text=["2", "4"] + [""] * (len(troughs) - 2),
            textposition="bottom center"
        ))

        st.plotly_chart(fig, use_container_width=True)

        # Optional GPT-based AI Summary
        if api_key:
            try:
                openai.api_key = api_key
                peak_vals = list(data["Close"].iloc[peaks][:3])
                trough_vals = list(data["Close"].iloc[troughs][:2])
                prompt = (
                    f"Given stock closing prices, peaks at {peak_vals} and troughs at {trough_vals}, "
                    f"analyze the Elliott Wave structure (Impulse + Corrective), and provide a short trading outlook."
                )

                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )

                st.subheader("🧠 AI Elliott Wave Summary")
                st.markdown(response["choices"][0]["message"]["content"])

            except Exception as e:
                st.error(f"🔒 OpenAI Error: {e}")
        else:
            st.info("Enter your OpenAI API key above to generate an AI summary.")

