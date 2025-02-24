import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pandas as pd

def create_price_chart(price_data):
    """Create a clean and modern price chart with white background."""
    if not price_data or not isinstance(price_data, list):
        return _create_error_figure("No price data available")

    try:
        # Convert to DataFrame with proper datetime handling
        df = pd.DataFrame(price_data)
        df['date'] = pd.to_datetime(df['timestamp'])
        df['price'] = df.apply(lambda x: float(x['quote']['USD']['price']), axis=1)
        df['volume'] = df.apply(lambda x: float(x['quote']['USD']['volume_24h']), axis=1)
        
        # Sort and remove duplicates
        df = df.sort_values('date').drop_duplicates('date')
        
        # Filter last 30 days
        cutoff_date = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=30)
        df = df[df['date'] >= cutoff_date]
        
        # Ensure continuous daily data
        date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')
        df = df.set_index('date').reindex(date_range).ffill()
        df = df.reset_index().rename(columns={'index': 'date'})

        # Calculate price direction
        price_color = '#16a34a' if df['price'].iloc[-1] >= df['price'].iloc[0] else '#dc2626'

        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            vertical_spacing=0.1,
            shared_xaxes=True
        )

        # Add price line
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['price'],
                name='Price',
                line=dict(
                    color=price_color,
                    width=1.5
                ),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>$%{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )

        # Add volume bars
        fig.add_trace(
            go.Bar(
                x=df['date'],
                y=df['volume'],
                name='Volume',
                marker_color='rgba(22, 163, 74, 0.3)',
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>$%{y:,.0f}<extra></extra>'
            ),
            row=2, col=1
        )

        # Update layout
        fig.update_layout(
            height=500,
            margin=dict(l=10, r=60, t=10, b=10),
            paper_bgcolor='white',
            plot_bgcolor='white',
            showlegend=False,
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor='white',
                bordercolor='#e5e5e5',
                font_size=12,
                font_color='#333333'
            )
        )

        # Configure x-axis
        fig.update_xaxes(
            row=2,
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.15)',
            tickfont=dict(size=10, color='#333333'),
            rangeslider_visible=False,
            dtick='D1',
            tickformat='%b %d'
        )

        # Hide x-axis for top subplot
        fig.update_xaxes(showticklabels=False, row=1)

        # Update y-axes
        fig.update_yaxes(
            row=1,
            tickprefix='$',
            tickformat=',.2f',
            side='right',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.15)',
            tickfont=dict(size=10, color='#333333')
        )

        fig.update_yaxes(
            row=2,
            tickprefix='$',
            tickformat=',.0f',
            side='right',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.15)',
            tickfont=dict(size=10, color='#333333')
        )

        # Add crosshair
        fig.update_xaxes(
            showspikes=True,
            spikecolor='rgba(0,0,0,0.2)',
            spikethickness=1
        )
        fig.update_yaxes(
            showspikes=True,
            spikecolor='rgba(0,0,0,0.2)',
            spikethickness=1
        )

        return fig

    except Exception as e:
        print(f"Error creating price chart: {str(e)}")
        return _create_error_figure(str(e))

def _create_error_figure(error_message):
    """Create a simple error figure with white background."""
    fig = go.Figure()
    fig.add_annotation(
        text=error_message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14, color='#333333')
    )
    fig.update_layout(
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig

def create_volume_chart(volume_data, top_n=10):
    """Create exchange volume breakdown chart."""
    if not volume_data or not isinstance(volume_data, list):
        return _create_error_figure("No volume data available")

    try:
        # Sort exchanges by volume
        sorted_data = sorted(volume_data, 
                           key=lambda x: x['quote']['USD']['volume_24h'], 
                           reverse=True)[:top_n]
        
        # Extract data
        exchanges = [pair['exchange']['name'] for pair in sorted_data]
        volumes = [pair['quote']['USD']['volume_24h'] for pair in sorted_data]
        
        # Calculate percentages for labels
        total_volume = sum(volumes)
        percentages = [v/total_volume * 100 for v in volumes]
        
        # Create labels with volume and percentage
        labels = [f"{ex}<br>{v:,.0f} USD ({p:.1f}%)" 
                 for ex, v, p in zip(exchanges, volumes, percentages)]

        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=volumes,
            hole=0.4,
            textinfo="label",
            textposition="outside",
            marker=dict(
                colors=px.colors.qualitative.Set3,
                line=dict(color='white', width=2)
            ),
            hovertemplate="<b>%{label}</b><br>" +
                         "Volume: $%{value:,.0f}<br>" +
                         "<extra></extra>"
        )])

        # Update layout
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            font=dict(size=12),
            title=dict(
                text="Exchange Volume Distribution",
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=16)
            )
        )

        return fig

    except Exception as e:
        print(f"Error creating volume chart: {str(e)}")
        return _create_error_figure(str(e))

def create_wallet_chart(wallet_data, wallet_name):
    """Create a detailed wallet balance and flow chart for the last 30 days"""
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add daily flows
    daily_flows = wallet_data.get('daily_flows', [])
    
    if not daily_flows:
        # Handle empty data case
        fig.add_annotation(
            text="No wallet data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
    
    # Filter for last 30 days
    cutoff_date = datetime.now() - timedelta(days=30)
    daily_flows = [
        flow for flow in daily_flows 
        if flow['date'] >= cutoff_date
    ]
    
    dates = [flow['date'] for flow in daily_flows]
    
    # Plot historical balance first (primary y-axis)
    # Calculate cumulative balance
    cumulative_balance = []
    balance = wallet_data['balance']
    for flow in reversed(daily_flows):
        balance -= flow['net_flow']
        cumulative_balance.append(balance)
    cumulative_balance.reverse()
    
    # Add balance line
    fig.add_trace(
        go.Scatter(
            name="Balance",
            x=dates,
            y=cumulative_balance,
            line=dict(color='rgb(52, 152, 219)', width=2),
            mode='lines',
        ),
        secondary_y=False,
    )

    # Plot daily flows (secondary y-axis)
    fig.add_trace(
        go.Bar(
            name="Inflows",
            x=dates,
            y=[flow['inflow'] for flow in daily_flows],
            marker=dict(
                color='rgb(46, 204, 113)',
                opacity=0.7
            ),
            offsetgroup=0
        ),
        secondary_y=True,
    )
    
    fig.add_trace(
        go.Bar(
            name="Outflows",
            x=dates,
            y=[flow['outflow'] for flow in daily_flows],
            marker=dict(
                color='rgb(231, 76, 60)',
                opacity=0.7
            ),
            offsetgroup=1
        ),
        secondary_y=True,
    )

    # Update layout
    fig.update_layout(
        title=dict(
            text=f"{wallet_name} Wallet Activity (Last 30 Days)",
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        template="plotly_dark",
        barmode='group',
        height=500,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=60, r=60, t=80, b=50),
        bargap=0.15,
        bargroupgap=0.1
    )

    # Customize axes
    fig.update_xaxes(
        title_text="Date",
        gridcolor='rgba(128,128,128,0.1)',
        showgrid=True,
        dtick='D1',  # Show daily ticks
        tickformat='%b %d'  # Format as "Mar 15"
    )

    # Set y-axes titles and format
    fig.update_yaxes(
        title_text="Wallet Balance (EGLD)",
        gridcolor='rgba(128,128,128,0.1)',
        showgrid=True,
        secondary_y=False,
        tickformat=",.0f",
        rangemode="tozero"
    )
    
    fig.update_yaxes(
        title_text="Daily Flows (EGLD)",
        gridcolor='rgba(128,128,128,0.1)',
        showgrid=True,
        secondary_y=True,
        tickformat=",.0f",
        rangemode="tozero"
    )

    # Improve hover information
    fig.update_traces(
        hovertemplate="<b>%{x|%b %d}</b><br>%{y:,.0f} EGLD<extra></extra>"
    )
    
    return fig

def create_tps_gauge(tps_value):
    """Create a gauge chart for TPS visualization"""
    
    # Define colors for different TPS ranges
    if tps_value < 10:
        color = "red"
    elif tps_value < 30:
        color = "orange"
    else:
        color = "green"

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = tps_value,
        number = {'suffix': " TPS", 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 10], 'color': 'rgba(255, 0, 0, 0.1)'},
                {'range': [10, 30], 'color': 'rgba(255, 165, 0, 0.1)'},
                {'range': [30, 100], 'color': 'rgba(0, 128, 0, 0.1)'}
            ],
        }
    ))

    fig.update_layout(
        height=150,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#808495"}
    )

    return fig

# Example usage with sample data
if __name__ == "__main__":
    # Sample price data
    sample_price_data = [
        {'timestamp': '2025-02-20T00:00:00.000Z', 'quote': {'USD': {'price': 100.5, 'volume_24h': 500000}}},
        {'timestamp': '2025-02-21T00:00:00.000Z', 'quote': {'USD': {'price': 102.3, 'volume_24h': 600000}}},
        {'timestamp': '2025-02-22T00:00:00.000Z', 'quote': {'USD': {'price': 101.8, 'volume_24h': 550000}}},
    ]

    # Sample volume data
    sample_volume_data = [
        {'exchange': {'name': 'Binance'}, 'quote': {'USD': {'volume_24h': 1000000}}},
        {'exchange': {'name': 'Coinbase'}, 'quote': {'USD': {'volume_24h': 750000}}},
        {'exchange': {'name': 'Kraken'}, 'quote': {'USD': {'volume_24h': 500000}}},
    ]

    # Sample wallet data
    sample_wallet_data = {
        'balance': 50.0,
        'transfers': [
            {'timestamp': '2025-02-20T10:00:00.000Z', 'value': 10.0, 'action': 'incoming'},
            {'timestamp': '2025-02-21T15:00:00.000Z', 'value': 5.0, 'action': 'outgoing'},
            {'timestamp': '2025-02-22T09:00:00.000Z', 'value': 15.0, 'action': 'incoming'},
            {'timestamp': '2025-02-22T12:00:00.000Z', 'value': 8.0, 'action': 'outgoing'},
        ]
    }

    # Generate and display charts
    price_fig = create_price_chart(sample_price_data)
    volume_fig = create_volume_chart(sample_volume_data, top_n=5)
    wallet_fig = create_wallet_chart(sample_wallet_data, "Sample Wallet")

    price_fig.show()
    volume_fig.show()
    wallet_fig.show()