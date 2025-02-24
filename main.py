import streamlit as st
from datetime import datetime
import time
import threading

# REFRESH LOGIC - MUST BE AT THE VERY TOP
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Check if 6 seconds have passed and force refresh
if (datetime.now() - st.session_state.last_refresh).seconds >= 6:
    st.session_state.last_refresh = datetime.now()
    st.rerun()

import plotly.graph_objects as go
import pandas as pd
import logging
import plotly.express as px
from streamlit.runtime.scriptrunner import get_script_run_ctx

from services.multiversx import MultiversXService
from services.coinmarketcap import CoinMarketCapService
from components.charts import create_price_chart, create_volume_chart, create_wallet_chart, create_tps_gauge
from components.metrics import display_metrics
from utils.cache import get_cached_data
from services.database import Database
from services.updater import start_updater, manual_update
from services.tps_updater import TPSUpdater
from components.tps_component import tps_gauge_component
from components.tps_display import tps_display

# Initialize session state
if 'tps_key' not in st.session_state:
    st.session_state['tps_key'] = 0

# Initialize TPS updater if not already done
if 'tps_updater' not in st.session_state:
    st.session_state.tps_updater = TPSUpdater()
    st.session_state.tps_updater.start()

def update_tps_gauge():
    """Callback to update only the TPS gauge"""
    st.session_state['tps_key'] += 1

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Page config
st.set_page_config(
    page_title="MultiversX Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Changed to collapsed since we're removing sidebar
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Set theme
st.markdown(f"""
    <script>
        document.body.setAttribute('data-theme', 'dark');
    </script>
    """, unsafe_allow_html=True)

# Initialize services
mx_service = MultiversXService()
cmc_service = CoinMarketCapService()

# Initialize database and start updater
db = Database()
start_updater()  # This starts the background task to update data every 10 minutes

# At the top of main.py, after imports
if 'tps_container' not in st.session_state:
    st.session_state.tps_container = st.empty()

# At the top of main.py, after imports
st.markdown("""
    <script>
        function refreshTPS() {
            const tpsGauge = document.getElementById('tps-gauge');
            if (tpsGauge) {
                tpsGauge.contentWindow.location.reload();
            }
        }
        setInterval(refreshTPS, 6000);
    </script>
""", unsafe_allow_html=True)

# Main content
st.title("MultiversX Network Overview")
st.markdown("Real-time insights into the MultiversX blockchain ecosystem")

# Network and Staking Statistics
st.markdown("### 🌐 Network & Staking Overview")
network_stats = get_cached_data('network_stats', mx_service.get_network_stats, ttl_minutes=5)
staking_stats = get_cached_data('staking_stats', mx_service.get_staking_stats, ttl_minutes=5)

# Create TPS container at the top level
if 'tps_container' not in st.session_state:
    st.session_state.tps_container = st.empty()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### Network Metrics")
    
    # Other metrics first
    st.metric("Total Transactions", f"{network_stats['transactions']:,}")
    st.metric("Total Accounts", f"{network_stats['active_addresses']:,}")
    
    # Create a placeholder for TPS gauge
    if 'tps_placeholder' not in st.session_state:
        st.session_state.tps_placeholder = st.empty()
    
    # Get current TPS
    current_tps = st.session_state.tps_updater.current_tps
    
    # Create gauge figure
    gauge_fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = current_tps,
        number = {'suffix': " TPS", 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 10], 'color': 'lightgray'},
                {'range': [10, 30], 'color': 'gray'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 30
            }
        }
    ))
    
    # Update layout
    gauge_fig.update_layout(
        height=150,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#808495"}
    )
    
    # Display gauge
    st.session_state.tps_placeholder.plotly_chart(
        gauge_fig, 
        use_container_width=True, 
        config={'displayModeBar': False}
    )
    
    # Force update every 6 seconds for just this component
    if 'last_tps_update' not in st.session_state:
        st.session_state.last_tps_update = time.time()
    
    if time.time() - st.session_state.last_tps_update >= 6:
        st.session_state.last_tps_update = time.time()
        st.session_state.tps_placeholder.empty()

with col2:
    st.markdown("#### Validator Statistics")
    st.metric("Total Validators", f"{staking_stats['total_validators']:,}")
    st.metric("Active Validators", f"{staking_stats['active_validators']:,}")
    st.metric("Eligible Validators", f"{staking_stats['eligible_validators']:,}")
    st.metric("Waiting Validators", f"{staking_stats['waiting_validators']:,}")
    st.metric("Total Observers", f"{staking_stats['total_observers']:,}")
    st.metric("Nakamoto Coefficient", f"{staking_stats['nakamoto_coefficient']}")

with col3:
    st.markdown("#### Staking Metrics")
    st.metric("Total Staked", f"{staking_stats['total_staked']:,.0f} EGLD")
    if staking_stats['staking_apr'] > 0:
        st.metric("Staking APR", f"{staking_stats['staking_apr']:.2f}%")
    else:
        st.metric("Staking APR", "N/A")

with col4:
    st.markdown("#### Legacy Staking")
    st.metric("Total Staking Users", f"{staking_stats['staking_users']:,}")
    st.metric("Active Stake", f"{staking_stats['total_active_stake']:,.0f} EGLD")
    st.metric("Waiting Stake", f"{staking_stats['total_waiting_stake']:,.0f} EGLD")
    st.metric("Unstaked", f"{staking_stats['total_unstaked']:,.0f} EGLD")
    st.metric("Deferred Payment", f"{staking_stats['total_deferred']:,.0f} EGLD")
    st.metric("Withdraw Only", f"{staking_stats['total_withdraw']:,.0f} EGLD")

    with st.expander("ℹ️ What is Nakamoto Coefficient?"):
        st.markdown("""
        The Nakamoto Coefficient represents the minimum number of validators 
        that would need to collude to control the network. A higher number 
        indicates better decentralization.
        """)

# Market metrics
with st.container():
    st.markdown("### 📈 Market Overview")
    col1, col2, col3, col4, col5 = st.columns(5)  # Added one more column
    market_data = get_cached_data('market_data', cmc_service.get_market_data, ttl_minutes=1)

    if all(v == 0 for v in market_data.values()):
        st.warning("⚠️ Unable to fetch market data. Please check back later.")

    # Define pastel colors
    pastel_green = "#98FB98"    # Mint green
    pastel_blue = "#B0E0E6"     # Powder blue
    pastel_purple = "#DCD0FF"   # Lavender
    pastel_pink = "#FFB6C1"     # Light pink
    pastel_orange = "#FFD8B1"   # Light orange

    # Background colors (lighter pastel)
    bg_pastel_green = "#E8F5E8"   # Light mint
    bg_pastel_blue = "#E6F3F5"    # Light powder blue
    bg_pastel_purple = "#F2EEFF"  # Light lavender
    bg_pastel_pink = "#FFF0F2"    # Light pink
    bg_pastel_orange = "#FFF3E6"  # Light orange

    # Custom CSS for metric styling
    st.markdown("""
        <style>
        .metric-container {
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .metric-label {
            color: #666666;
            font-size: 0.9rem;
            margin-bottom: 5px;
            font-weight: 500;
        }
        .metric-value {
            font-size: 1.2rem;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # Display market metrics with pastel colors
    with col1:
        st.markdown(f"""
            <div class="metric-container" style="background-color: {bg_pastel_green};">
                <div class="metric-label">Current Price</div>
                <div class="metric-value" style="color: #2E8B57;">${market_data['price']}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-container" style="background-color: {bg_pastel_blue};">
                <div class="metric-label">24h Volume</div>
                <div class="metric-value" style="color: #4682B4;">${market_data['volume_24h']:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-container" style="background-color: {bg_pastel_purple};">
                <div class="metric-label">Market Cap</div>
                <div class="metric-value" style="color: #6A5ACD;">${market_data['market_cap']:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="metric-container" style="background-color: {bg_pastel_pink};">
                <div class="metric-label">Circulating Supply</div>
                <div class="metric-value" style="color: #DB7093;">{market_data['circulating_supply']:,.0f} EGLD</div>
            </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
            <div class="metric-container" style="background-color: {bg_pastel_orange};">
                <div class="metric-label">CMC Rank</div>
                <div class="metric-value" style="color: #FF8C00;">#{market_data.get('cmc_rank', 'N/A')}</div>
            </div>
        """, unsafe_allow_html=True)

# Replace the current price chart section with TradingView widget
st.markdown("### 📈 Price Chart")

# Add TradingView widget
tradingview_widget = """
<div class="tradingview-widget-container">
  <div id="tradingview_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "width": "100%",
    "height": 500,
    "symbol": "BINANCE:EGLDUSDT",
    "interval": "D",
    "timezone": "Etc/UTC",
    "theme": "light",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "container_id": "tradingview_chart"
  });
  </script>
</div>
"""

# Display TradingView chart
st.components.v1.html(tradingview_widget, height=600)

# Add chart context
with st.expander("💡 About This Chart"):
    st.markdown("""
    This is a professional TradingView chart showing:
    - EGLD/USDT price from Binance
    - Interactive charting tools
    
    You can:
    - Change timeframes
    - Add technical indicators
    - Draw trendlines
    - Compare with other assets
    """)

# Charts section
st.markdown("### 📊 Market Analysis")

# Volume Distribution Chart
volume_data = get_cached_data('volume_data',
                             lambda: cmc_service.get_exchange_volumes(),
                             ttl_minutes=5)

if volume_data:
    fig = create_volume_chart(volume_data)
    st.plotly_chart(fig, use_container_width=True, key="volume_distribution_chart")

    with st.expander("💡 Understanding Volume Distribution"):
        st.markdown("""
        This chart shows the distribution of EGLD trading volume across major exchanges:
        - Larger segments indicate higher trading activity
        - Helps identify the most liquid exchanges
        - Can indicate market maker presence
        """)
else:
    st.error("Unable to fetch volume distribution data")

# Exchange Wallets Monitor Section
st.markdown("### 💰 Exchange Wallets Monitor")

# Exchange wallet addresses and data fetching
binance_address = "erd1sdslvlxvfnnflzj42l8czrcngq3xjjzkjp3rgul4ttk6hntr4qdsv6sets"
binance_data = get_cached_data(
    'binance_wallet',
    lambda: mx_service.get_wallet_balance(binance_address),
    ttl_minutes=5
)

bybit_address = "erd1vj3efd5czwearu0gr3vjct8ef53lvtl7vs42vts2kh2qn3cucrnsj7ymqx"
bybit_data = get_cached_data(
    'bybit_wallet',
    lambda: mx_service.get_wallet_balance(bybit_address),
    ttl_minutes=5
)

upbit_address = "erd1hqamcl7hacu28q0l2kh7jt0vs6tjfhq4vp2tv7hufkx3phu0jn5ql3qw7x"
upbit_data = get_cached_data(
    'upbit_wallet',
    lambda: mx_service.get_wallet_balance(upbit_address),
    ttl_minutes=5
)

gateio_address = "erd1p4vy5n9mlkdys7xczegj398xtyvw2nawz00nnfh4yr7fpjh297cqtsu7lw"
gateio_data = get_cached_data(
    'gateio_wallet',
    lambda: mx_service.get_wallet_balance(gateio_address),
    ttl_minutes=5
)

bitfinex_address = "erd1a56dkgcpwwx6grmcvw9w5vpf9zeq53w3w7n6dmxcpxjry3l7uh2s3h9dtr"
bitfinex_data = get_cached_data(
    'bitfinex_wallet',
    lambda: mx_service.get_wallet_balance(bitfinex_address),
    ttl_minutes=5
)

cryptocom_address = "erd1hzccjg25yqaqnr732x2ka7pj5glx72pfqzf05jj9hxqn3lxkramq5zu8h4"
cryptocom_data = get_cached_data(
    'cryptocom_wallet',
    lambda: mx_service.get_wallet_balance(cryptocom_address),
    ttl_minutes=5
)

kraken_address = "erd1nmtkpqzhkla5yreu2dlyzm9fm8v902wjhvzu7xjjkd8ppefmtlws7qvx2a"
kraken_data = get_cached_data(
    'kraken_wallet',
    lambda: mx_service.get_wallet_balance(kraken_address),
    ttl_minutes=5
)

bitget_address = "erd1w547kw69kpd60vlpr9pe0pn9nnqeljrcaz73znenjpgt0h3qlqqqm3szxj"
bitget_data = get_cached_data(
    'bitget_wallet',
    lambda: mx_service.get_wallet_balance(bitget_address),
    ttl_minutes=5
)

mexc_address = "erd1ezp86jwmcp4fmmu2mfqz0438py392z5wp6kzuqsjldgd68nwt89qshfs0y"
mexc_data = get_cached_data(
    'mexc_wallet',
    lambda: mx_service.get_wallet_balance(mexc_address),
    ttl_minutes=5
)

kucoin_address = "erd1ty4pvmjtl3mnsjvnsxgcpedd08fsn83f05tu0v5j23wnfce9p86snlkdyy"
kucoin_data = get_cached_data(
    'kucoin_wallet',
    lambda: mx_service.get_wallet_balance(kucoin_address),
    ttl_minutes=5
)

kucoin_cold_address = "erd1vtlpm6sxxvmgt43ldsrpswjrfcsudmradylpxn9jkp66ra3rkz4qruzvfw"
kucoin_cold_data = get_cached_data(
    'kucoin_cold_wallet',
    lambda: mx_service.get_wallet_balance(kucoin_cold_address),
    ttl_minutes=5
)

# Add Coinbase cold wallet fetch
coinbase_cold_address = "erd16xta8867juxzm0sqmfevpa5karkd3l5k9cspns6zj28auv7nugqqpph374"
coinbase_cold_data = get_cached_data(
    'coinbase_cold_wallet',
    lambda: mx_service.get_wallet_balance(coinbase_cold_address),
    ttl_minutes=5
)

# Update exchanges_data dictionary
exchanges_data = {
    'Binance Hot': binance_data,
    'Binance Cold': coinbase_cold_data,
    'ByBit': bybit_data,
    'Upbit': upbit_data,
    'Gate.io': gateio_data,
    'Bitfinex': bitfinex_data,
    'Crypto.com': cryptocom_data,
    'Kraken': kraken_data,
    'KuCoin Hot': kucoin_data,
    'KuCoin Cold': kucoin_cold_data,
    'Bitget': bitget_data,
    'MEXC': mexc_data,
    'Coinbase Hot': binance_data,
    'Coinbase Cold': coinbase_cold_data
}

# Now create the summary section first
st.markdown("#### 📊 Exchanges Summary")

# Calculate total metrics across all exchanges
total_balance = sum(data['balance'] for data in exchanges_data.values())

# Create metrics columns
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Exchange Balance", f"{total_balance:,.2f} EGLD")

# Calculate 24h flows across all exchanges
total_inflow = 0
total_outflow = 0
for data in exchanges_data.values():
    recent_transfers = [
        tx for tx in data['transfers'] 
        if (datetime.now() - tx['timestamp']).days < 1
    ]
    
    total_inflow += sum(
        tx['value'] for tx in recent_transfers 
        if tx['action'] == 'incoming'
    )
    
    total_outflow += sum(
        tx['value'] for tx in recent_transfers 
        if tx['action'] == 'outgoing'
    )

with col2:
    st.metric(
        "24h Total Inflow",
        f"{total_inflow:,.2f} EGLD",
        f"↑ {total_inflow:,.2f} EGLD" if total_inflow > 0 else "No inflow"
    )

with col3:
    st.metric(
        "24h Total Outflow",
        f"{total_outflow:,.2f} EGLD",
        f"↓ {total_outflow:,.2f} EGLD" if total_outflow > 0 else "No outflow"
    )

# Add exchange distribution table
st.markdown("#### Exchange Distribution")

# Add custom CSS for table styling
st.markdown("""
    <style>
        .dataframe {
            width: 100% !important;
            margin-bottom: 20px;
        }
        .dataframe td, .dataframe th {
            white-space: nowrap;
            padding: 8px;
            text-align: left;
        }
        .dataframe th {
            background-color: #f0f2f6;
        }
    </style>
""", unsafe_allow_html=True)

# Create mapping of exchange names to their addresses
exchange_addresses = {
    'Binance Hot': 'erd1sdslvlxvfnnflzj42l8czrcngq3xjjzkjp3rgul4ttk6hntr4qdsv6sets',
    'Binance Cold': 'erd1v4ms58e22zjcp08suzqgm9ajmumwxcy4hfkdc23gvynnegjdflmsj6gmaq',
    'ByBit': 'erd1vj3efd5czwearu0gr3vjct8ef53lvtl7vs42vts2kh2qn3cucrnsj7ymqx',
    'Upbit': 'erd1hqamcl7hacu28q0l2kh7jt0vs6tjfhq4vp2tv7hufkx3phu0jn5ql3qw7x',
    'Gate.io': 'erd1p4vy5n9mlkdys7xczegj398xtyvw2nawz00nnfh4yr7fpjh297cqtsu7lw',
    'Bitfinex': 'erd1a56dkgcpwwx6grmcvw9w5vpf9zeq53w3w7n6dmxcpxjry3l7uh2s3h9dtr',
    'Crypto.com': 'erd1hzccjg25yqaqnr732x2ka7pj5glx72pfqzf05jj9hxqn3lxkramq5zu8h4',
    'Kraken': 'erd1nmtkpqzhkla5yreu2dlyzm9fm8v902wjhvzu7xjjkd8ppefmtlws7qvx2a',
    'KuCoin Hot': 'erd1ty4pvmjtl3mnsjvnsxgcpedd08fsn83f05tu0v5j23wnfce9p86snlkdyy',
    'KuCoin Cold': 'erd1vtlpm6sxxvmgt43ldsrpswjrfcsudmradylpxn9jkp66ra3rkz4qruzvfw',
    'Bitget': 'erd1w547kw69kpd60vlpr9pe0pn9nnqeljrcaz73znenjpgt0h3qlqqqm3szxj',
    'MEXC': 'erd1ezp86jwmcp4fmmu2mfqz0438py392z5wp6kzuqsjldgd68nwt89qshfs0y',
    'Coinbase Hot': 'erd16jruked88jgtsar78ej85hjp3qsd9jkjcw4swsn7k0teqh3wgcqqgyrupq',
    'Coinbase Cold': 'erd16xta8867juxzm0sqmfevpa5karkd3l5k9cspns6zj28auv7nugqqpph374'
}

# Calculate percentages and create table data
distribution_data = []
for exchange, data in exchanges_data.items():
    percentage = (data['balance'] / total_balance * 100) if total_balance > 0 else 0
    # Create clickable link for exchange name using HTML
    exchange_link = f'<a href="https://explorer.multiversx.com/accounts/{exchange_addresses[exchange]}" target="_blank">{exchange}</a>'
    distribution_data.append({
        "Exchange": exchange_link,
        "Balance": f"{data['balance']:,.2f} EGLD",
        "Percentage": f"{percentage:.2f}%"
    })

# Sort by balance descending
distribution_data.sort(key=lambda x: float(x['Balance'].replace(',', '').split()[0]), reverse=True)

# Create a DataFrame
df = pd.DataFrame(distribution_data)

# Display the table with HTML rendering and custom styling
st.write(
    df.to_html(
        escape=False,
        index=False,
        justify='left',
        classes='dataframe',
        border=0
    ),
    unsafe_allow_html=True
)

# Add a pie chart for visual representation
fig = go.Figure(data=[go.Pie(
    labels=[d['Exchange'] for d in distribution_data],
    values=[float(d['Balance'].replace(',', '').split()[0]) for d in distribution_data],
    hole=0.4,
    textinfo='percent+label',
    hovertemplate="<b>%{label}</b><br>" +
                  "Balance: %{value:,.2f} EGLD<br>" +
                  "Share: %{percent}<extra></extra>",
    marker=dict(
        colors=px.colors.qualitative.Set3,
        line=dict(color='white', width=2)
    ),
    textposition='outside',
    pull=[0.1 if 'Binance' in label else 0 for label in [d['Exchange'] for d in distribution_data]]
)])

fig.update_layout(
    title="Exchange Balance Distribution",
    height=600,
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    margin=dict(l=20, r=20, t=40, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(size=12)
)

st.plotly_chart(fig, use_container_width=True, key="exchange_distribution_pie")

# Now display individual wallet sections
st.markdown("#### Individual Exchange Wallets")

# Add unique keys to all wallet charts
exchange_sections = {
    'Binance Hot Wallet': ('binance_chart', binance_data),
    'ByBit Hot Wallet': ('bybit_chart', bybit_data),
    'Upbit Hot Wallet': ('upbit_chart', upbit_data),
    'Gate.io Hot Wallet': ('gateio_chart', gateio_data),
    'Bitfinex Hot Wallet': ('bitfinex_chart', bitfinex_data),
    'Crypto.com Hot Wallet': ('cryptocom_chart', cryptocom_data),
    'Kraken Hot Wallet': ('kraken_chart', kraken_data),
    'KuCoin Hot Wallet': ('kucoin_chart', kucoin_data),
    'Bitget Hot Wallet': ('bitget_chart', bitget_data),
    'MEXC Hot Wallet': ('mexc_chart', mexc_data),
    'Coinbase Hot Wallet': ('coinbase_chart', binance_data)
}

# Display individual wallet sections
for title, (chart_key, data) in exchange_sections.items():
    st.markdown(f"#### {title}")
    col1, col2 = st.columns([3, 1])

    with col1:
        fig = create_wallet_chart(data, title.replace(" Hot Wallet", ""))
        st.plotly_chart(fig, use_container_width=True, key=chart_key)

    with col2:
        st.metric(
            "Current Balance",
            f"{data['balance']:,.2f} EGLD"
        )
        
        # Calculate 24h flows
        recent_transfers = [
            tx for tx in data['transfers'] 
            if (datetime.now() - tx['timestamp']).days < 1
        ]
        
        # Calculate previous day flows
        prev_day_transfers = [
            tx for tx in data['transfers'] 
            if 1 <= (datetime.now() - tx['timestamp']).days < 2
        ]
        
        # Current day flows
        inflow_24h = sum(
            tx['value'] for tx in recent_transfers 
            if tx['action'] == 'incoming'
        )
        outflow_24h = sum(
            tx['value'] for tx in recent_transfers 
            if tx['action'] == 'outgoing'
        )
        
        # Previous day flows
        inflow_prev = sum(
            tx['value'] for tx in prev_day_transfers 
            if tx['action'] == 'incoming'
        ) or 1  # Avoid division by zero
        outflow_prev = sum(
            tx['value'] for tx in prev_day_transfers 
            if tx['action'] == 'outgoing'
        ) or 1  # Avoid division by zero
        
        # Calculate percentage changes
        inflow_change = ((inflow_24h - inflow_prev) / inflow_prev) * 100
        outflow_change = ((outflow_24h - outflow_prev) / outflow_prev) * 100
        
        st.metric(
            "24h Inflow",
            f"{inflow_24h:,.2f} EGLD",
            f"{inflow_change:+.1f}% vs yesterday" if inflow_prev > 1 else "N/A",
            delta_color="normal"
        )
        
        st.metric(
            "24h Outflow",
            f"{outflow_24h:,.2f} EGLD",
            f"{outflow_change:+.1f}% vs yesterday" if outflow_prev > 1 else "N/A",
            delta_color="inverse"
        )
        
        net_24h_change = inflow_24h - outflow_24h
        st.metric(
            "24h Net Flow",
            f"{abs(net_24h_change):,.2f} EGLD",
            f"{'↑' if net_24h_change > 0 else '↓'} Net {abs(net_24h_change):,.2f} EGLD",
            delta_color="normal" if net_24h_change > 0 else "inverse"
        )

        with st.expander("ℹ️ About this Wallet"):
            st.markdown("""
            This is {title} for EGLD. It handles:
            - User deposits and withdrawals
            - Internal transfers
            - Exchange operations
            
            [View on Explorer](https://explorer.multiversx.com/accounts/{address})
            """)

# Add this temporarily to check database status
if st.sidebar.button("Check Database"):
    db = Database()
    if db.check_connection():
        stats = db.get_stats()
        st.sidebar.write("Database Statistics:")
        st.sidebar.write(f"Wallet records: {stats['wallet_records']}")
        st.sidebar.write(f"Market records: {stats['market_records']}")
        st.sidebar.write(f"Network records: {stats['network_records']}")
        st.sidebar.write(f"Last wallet update: {stats['last_wallet_update']}")
    db.close()

if st.sidebar.button("Update Data Now"):
    manual_update()
    st.sidebar.success("Data updated successfully!")

# Add a placeholder for auto-refresh indicator
placeholder = st.empty()
with placeholder.container():
    st.markdown(f"_Last updated: {datetime.now().strftime('%H:%M:%S')}_")

# Create a function to get TPS that will be called periodically
def get_current_tps():
    if 'tps_updater' in st.session_state:
        return st.session_state.tps_updater.current_tps
    return 0

# At the top of main.py, after imports
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0

# Increment counter and trigger rerun every 6 seconds
if time.time() % 6 < 0.1:  # Check if we're at the start of a 6-second interval
    st.session_state.refresh_counter += 1
    st.rerun()

# Create a function to auto-refresh the page
def auto_refresh():
    time.sleep(6)
    st.experimental_rerun()