import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_price_chart(price_data):
    """Create price and volume chart"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Price", "Volume"),
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )

    fig.add_trace(
        go.Scatter(
            x=[quote['timestamp'] for quote in price_data],
            y=[quote['quote']['USD']['price'] for quote in price_data],
            mode='lines',
            name='Price',
            line=dict(color='#1f77b4')
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            x=[quote['timestamp'] for quote in price_data],
            y=[quote['quote']['USD']['volume_24h'] for quote in price_data],
            name='Volume',
            marker_color='#2ca02c'
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=600,
        showlegend=False,
        template='plotly_dark',
        margin=dict(l=0, r=0, t=30, b=0)
    )

    return fig

def create_volume_chart(volume_data):
    """Create exchange volume breakdown chart"""
    exchanges = [pair['exchange']['name'] for pair in volume_data[:10]]
    volumes = [pair['quote']['USD']['volume_24h'] for pair in volume_data[:10]]

    fig = go.Figure(data=[
        go.Pie(
            labels=exchanges,
            values=volumes,
            hole=0.4,
            marker=dict(colors=px.colors.sequential.Blues)
        )
    ])

    fig.update_layout(
        height=400,
        template='plotly_dark',
        margin=dict(l=0, r=0, t=30, b=0)
    )

    return fig
