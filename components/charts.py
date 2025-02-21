import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def create_price_chart(price_data):
    """Create price and volume chart"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("EGLD Price (USD)", "Trading Volume (USD)"),
        vertical_spacing=0.12,
        row_heights=[0.7, 0.3]
    )

    # Price trace
    fig.add_trace(
        go.Scatter(
            x=[quote['timestamp'] for quote in price_data],
            y=[quote['quote']['USD']['price'] for quote in price_data],
            mode='lines',
            name='Price',
            line=dict(color='#1f77b4', width=2),
            hovertemplate="<b>Price:</b> $%{y:.2f}<br>" +
                         "<b>Time:</b> %{x}<br><extra></extra>"
        ),
        row=1, col=1
    )

    # Volume trace
    fig.add_trace(
        go.Bar(
            x=[quote['timestamp'] for quote in price_data],
            y=[quote['quote']['USD']['volume_24h'] for quote in price_data],
            name='Volume',
            marker_color='rgba(44, 160, 44, 0.5)',
            hovertemplate="<b>Volume:</b> $%{y:,.0f}<br>" +
                         "<b>Time:</b> %{x}<br><extra></extra>"
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=600,
        showlegend=False,
        template='plotly_dark',
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis2_showgrid=False,
        yaxis_gridcolor='rgba(128,128,128,0.1)',
        yaxis2_gridcolor='rgba(128,128,128,0.1)',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Roboto"
        )
    )

    # Update axes labels
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Volume (USD)", row=2, col=1)

    return fig

def create_volume_chart(volume_data):
    """Create exchange volume breakdown chart"""
    exchanges = [pair['exchange']['name'] for pair in volume_data[:10]]
    volumes = [pair['quote']['USD']['volume_24h'] for pair in volume_data[:10]]

    # Calculate percentages for hover text
    total_volume = sum(volumes)
    percentages = [f"{(v/total_volume)*100:.1f}%" for v in volumes]

    fig = go.Figure(data=[
        go.Pie(
            labels=exchanges,
            values=volumes,
            hole=0.4,
            marker=dict(colors=px.colors.sequential.Blues),
            textinfo='label+percent',
            hovertemplate="<b>%{label}</b><br>" +
                         "Volume: $%{value:,.0f}<br>" +
                         "Share: %{percent}<br>" +
                         "<extra></extra>",
            textfont=dict(size=12)
        )
    ])

    fig.update_layout(
        height=400,
        template='plotly_dark',
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        annotations=[dict(
            text="24h Trading Volume Distribution",
            x=0.5,
            y=1.1,
            showarrow=False,
            font=dict(size=14)
        )],
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Roboto"
        )
    )

    return fig