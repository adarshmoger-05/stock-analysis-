import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import datetime

# Set Streamlit page config
st.set_page_config(page_title="📈 Live Stock Market Dashboard", layout="wide")

st.title("📊 Live Stock Market Dashboard")
st.markdown("View real-time stock prices, closing trends, and trading volume.")

# Sidebar input
symbols = st.sidebar.multiselect(
    "Select Stocks to View",
    ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "IBM", "INTC"],
    default=["AAPL", "MSFT", "GOOGL"]
)

start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

# Load stock data
if symbols:
    all_data = yf.download(symbols, start=start_date, end=end_date)

    # Flatten multi-index columns
    all_data.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in all_data.columns]
    all_data.reset_index(inplace=True)

    st.subheader("📅 Raw Data Preview")
    st.dataframe(all_data.head(), use_container_width=True)

    # Closing Price Trend
    st.subheader("📈 Closing Price Trend")
    fig1 = px.line()
    for symbol in symbols:
        fig1.add_scatter(
            x=all_data['Date'],
            y=all_data[f'Close_{symbol}'],
            mode='lines',
            name=symbol
        )
    fig1.update_layout(title="Closing Price Over Time", xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig1, use_container_width=True)

    # Volume Traded
    st.subheader("📊 Volume Traded")
    fig2 = px.area()
    for symbol in symbols:
        fig2.add_scatter(
            x=all_data['Date'],
            y=all_data[f'Volume_{symbol}'],
            mode='lines',
            stackgroup='one',
            name=symbol
        )
    fig2.update_layout(title="Daily Volume Traded", xaxis_title="Date", yaxis_title="Volume")
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.warning("👈 Please select at least one stock symbol to view data.")
