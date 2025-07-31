import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import datetime

# Streamlit page setup
st.set_page_config(page_title="📈 Live Stock Market Dashboard", layout="wide")
st.title("📊 Live Stock Market Dashboard")
st.markdown("View real-time stock prices, candlestick charts, trends, and volume with optional moving averages.")

# Sidebar - Inputs
default_symbols = ["AAPL", "MSFT", "GOOGL"]
symbol_input = st.sidebar.text_input("Enter stock symbols (comma-separated):", value=", ".join(default_symbols))
symbols = [sym.strip().upper() for sym in symbol_input.split(",") if sym.strip()]

start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())
show_ma = st.sidebar.checkbox("Show 7-Day Moving Average", value=True)

# Cached function to load data
@st.cache_data
def load_stock_data(symbols, start, end):
    return yf.download(symbols, start=start, end=end, group_by='ticker', auto_adjust=True)

# Check and fetch data
if symbols:
    with st.spinner("⏳ Loading data..."):
        try:
            raw_data = load_stock_data(symbols, start_date, end_date)
        except Exception as e:
            st.error(f"Failed to fetch stock data: {e}")
            st.stop()

    # Process data
    if len(symbols) == 1:
        df = raw_data.copy()
        df.reset_index(inplace=True)
        st.subheader("📅 Raw Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        # 🕯️ Candlestick Chart
        st.subheader(f"🕯️ {symbols[0]} Candlestick Chart")
        fig_candle = go.Figure(data=[
            go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=symbols[0]
            )
        ])
        fig_candle.update_layout(
            title=f"{symbols[0]} Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Price (USD)"
        )
        st.plotly_chart(fig_candle, use_container_width=True)

        # 📈 Closing Price with Optional MA
        st.subheader(f"📈 {symbols[0]} Closing Price")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close'))

        if show_ma:
            ma = df['Close'].rolling(window=7).mean()
            fig_line.add_trace(go.Scatter(x=df['Date'], y=ma, mode='lines', name='7-Day MA', line=dict(dash='dash')))

        fig_line.update_layout(title="Closing Price Trend", xaxis_title="Date", yaxis_title="Price (USD)")
        st.plotly_chart(fig_line, use_container_width=True)

        # 📊 Volume
        st.subheader("📊 Volume Traded")
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name="Volume"))
        fig_vol.update_layout(title="Trading Volume", xaxis_title="Date", yaxis_title="Volume")
        st.plotly_chart(fig_vol, use_container_width=True)

        # 📥 Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Data as CSV", data=csv, file_name=f"{symbols[0]}_stock_data.csv", mime='text/csv')

    else:
        # Multiple stocks view
        df = pd.DataFrame()
        for symbol in symbols:
            stock_df = raw_data[symbol].copy()
            stock_df['Symbol'] = symbol
            stock_df['Date'] = stock_df.index
            df = pd.concat([df, stock_df], ignore_index=True)

        st.subheader("📅 Raw Data Preview")
        st.dataframe(df[['Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']].head(), use_container_width=True)

        # 📈 Closing Price Comparison
        st.subheader("📈 Closing Price Trend Comparison")
        fig_multi = go.Figure()
        for symbol in symbols:
            symbol_data = raw_data[symbol].copy()
            fig_multi.add_trace(go.Scatter(
                x=symbol_data.index,
                y=symbol_data['Close'],
                mode='lines',
                name=symbol
            ))
        fig_multi.update_layout(title="Closing Price Over Time", xaxis_title="Date", yaxis_title="Price (USD)")
        st.plotly_chart(fig_multi, use_container_width=True)

        # 📊 Volume Comparison
        st.subheader("📊 Volume Comparison")
        fig_vol = go.Figure()
        for symbol in symbols:
            symbol_data = raw_data[symbol].copy()
            fig_vol.add_trace(go.Scatter(
                x=symbol_data.index,
                y=symbol_data['Volume'],
                mode='lines',
                name=symbol,
                stackgroup='one'
            ))
        fig_vol.update_layout(title="Volume Traded Over Time", xaxis_title="Date", yaxis_title="Volume")
        st.plotly_chart(fig_vol, use_container_width=True)

        # 📥 Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Data as CSV", data=csv, file_name="multi_stock_data.csv", mime='text/csv')
else:
    st.warning("👈 Please enter at least one valid stock symbol.")
