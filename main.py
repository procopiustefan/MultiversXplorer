import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

from services.multiversx import MultiversXService
from services.coinmarketcap import CoinMarketCapService
from components.charts import create_price_chart, create_volume_chart
from components.metrics import display_metrics
from utils.cache import get_cached_data

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

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

# Set theme
st.markdown(f"""
    <script>
        document.body.setAttribute('data-theme', '{st.session_state.theme}');
    </script>
    """, unsafe_allow_html=True)

# Initialize services
mx_service = MultiversXService()
cmc_service = CoinMarketCapService()

# Sidebar
st.sidebar.title("MultiversX Explorer")
st.sidebar.markdown("---")

# Theme toggle
theme = st.sidebar.selectbox(
    "🎨 Theme",
    ["Dark", "Light"],
    index=0 if st.session_state.theme == 'dark' else 1
)
st.session_state.theme = theme.lower()

timeframe = st.sidebar.selectbox(
    "📅 Timeframe",
    ["24h", "7d", "30d", "90d"],
    index=1  # Default to 7d
)

# Main content
st.title("MultiversX Network Overview")
st.markdown("Real-time insights into the MultiversX blockchain ecosystem")

# Network and Staking Statistics first
st.markdown("### 🌐 Network & Staking Overview")
network_stats = get_cached_data('network_stats', mx_service.get_network_stats)
staking_stats = get_cached_data('staking_stats', mx_service.get_staking_stats)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Network Metrics")
    st.metric("Total Transactions", f"{network_stats['transactions']:,}")
    st.metric("Active Addresses", f"{network_stats['active_addresses']:,}")
    st.metric("Network Speed", f"{network_stats['tps']} TPS")

with col2:
    st.markdown("#### Validator Statistics")
    st.metric("Total Validators", f"{staking_stats['total_validators']:,}")
    st.metric("Active Validators", f"{staking_stats['active_validators']:,}")
    st.metric("Total Observers", f"{staking_stats['total_observers']:,}")

with col3:
    st.markdown("#### Staking Metrics")
    st.metric("Total Staked", f"{staking_stats['total_staked']:,.0f} EGLD")
    st.metric("Staking APR", f"{network_stats['staking_apr']}%")
    st.metric("Nakamoto Coefficient", staking_stats['nakamoto_coefficient'])

    with st.expander("ℹ️ What is Nakamoto Coefficient?"):
        st.markdown("""
        The Nakamoto Coefficient represents the minimum number of validators 
        that would need to collude to control the network. A higher number 
        indicates better decentralization.
        """)

# Market metrics
with st.container():
    st.markdown("### 📈 Market Overview")
    col1, col2, col3, col4 = st.columns(4)
    market_data = get_cached_data('market_data', cmc_service.get_market_data)

    if all(v == 0 for v in market_data.values()):
        st.warning("⚠️ Unable to fetch market data. Please check back later.")

    with col1:
        display_metrics("Current Price", f"${market_data['price']:.2f}")
    with col2:
        display_metrics("24h Volume", f"${market_data['volume_24h']:,.0f}")
    with col3:
        display_metrics("Market Cap", f"${market_data['market_cap']:,.0f}")
    with col4:
        display_metrics("Circulating Supply", f"{market_data['circulating_supply']:,.0f} EGLD")

# Charts section
st.markdown("### 📊 Market Analysis")
tab1, tab2 = st.tabs(["Price Analysis", "Volume Distribution"])

with tab1:
    price_data = get_cached_data('price_data', 
                                lambda: cmc_service.get_historical_data(timeframe))
    fig = create_price_chart(price_data)
    st.plotly_chart(fig, use_container_width=True)

    # Add price analysis context
    with st.expander("💡 Understanding the Price Chart"):
        st.markdown("""
        - The top chart shows the EGLD price movement over time
        - The bottom chart displays trading volume, indicating market activity
        - Higher volume often correlates with significant price movements
        """)

with tab2:
    volume_data = get_cached_data('volume_data',
                                 lambda: cmc_service.get_exchange_volumes())
    fig = create_volume_chart(volume_data)
    st.plotly_chart(fig, use_container_width=True)

    # Add volume analysis context
    with st.expander("💡 Understanding Volume Distribution"):
        st.markdown("""
        - Shows the distribution of trading volume across major exchanges
        - Larger segments indicate higher trading activity on that exchange
        - A well-distributed volume suggests healthy market liquidity
        """)

# Recent Transactions
st.markdown("### 🔄 Recent Transactions")
transactions = get_cached_data('recent_transactions', 
                             mx_service.get_recent_transactions)

if not transactions:
    st.info("No recent transactions available at the moment.")
else:
    for tx in transactions[:10]:
        with st.expander(f"Transaction {tx['hash'][:10]}..."):
            st.markdown(f"""
            **From:** `{tx['from']}`  
            **To:** `{tx['to']}`  
            **Amount:** {tx['amount']} EGLD  
            **Time:** {tx['timestamp']}
            """)