import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

from services.multiversx import MultiversXService
from services.coinmarketcap import CoinMarketCapService
from components.charts import create_price_chart, create_volume_chart
from components.metrics import display_metrics
from utils.cache import get_cached_data

# Page config
st.set_page_config(
    page_title="MultiversX Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize services
mx_service = MultiversXService()
cmc_service = CoinMarketCapService()

# Sidebar
st.sidebar.title("MultiversX Explorer")
search_query = st.sidebar.text_input("Search Transactions/Addresses")
timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["24h", "7d", "30d", "90d"]
)

# Main content
st.title("MultiversX Network Overview")

# Market metrics
col1, col2, col3, col4 = st.columns(4)
market_data = get_cached_data('market_data', cmc_service.get_market_data)

with col1:
    display_metrics("Price", f"${market_data['price']:.2f}")
with col2:
    display_metrics("24h Volume", f"${market_data['volume_24h']:,.0f}")
with col3:
    display_metrics("Market Cap", f"${market_data['market_cap']:,.0f}")
with col4:
    display_metrics("Circulating Supply", f"{market_data['circulating_supply']:,.0f} EGLD")

# Charts
st.subheader("Price & Volume Analysis")
tab1, tab2 = st.tabs(["Price Chart", "Volume Breakdown"])

with tab1:
    price_data = get_cached_data('price_data', 
                                lambda: cmc_service.get_historical_data(timeframe))
    fig = create_price_chart(price_data)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    volume_data = get_cached_data('volume_data',
                                 lambda: cmc_service.get_exchange_volumes())
    fig = create_volume_chart(volume_data)
    st.plotly_chart(fig, use_container_width=True)

# Network Statistics
st.subheader("Network Statistics")
col1, col2 = st.columns(2)

with col1:
    network_stats = get_cached_data('network_stats', mx_service.get_network_stats)
    st.metric("Total Transactions", f"{network_stats['transactions']:,}")
    st.metric("Active Addresses", f"{network_stats['active_addresses']:,}")

with col2:
    st.metric("Network Speed", f"{network_stats['tps']} TPS")
    st.metric("Staking APR", f"{network_stats['staking_apr']:.2f}%")

# Recent Transactions
st.subheader("Recent Transactions")
transactions = get_cached_data('recent_transactions', 
                             mx_service.get_recent_transactions)

for tx in transactions[:10]:
    with st.expander(f"Transaction {tx['hash'][:10]}..."):
        st.write(f"From: {tx['from']}")
        st.write(f"To: {tx['to']}")
        st.write(f"Amount: {tx['amount']} EGLD")
        st.write(f"Time: {tx['timestamp']}")
