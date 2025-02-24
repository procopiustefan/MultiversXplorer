import streamlit as st

def display_metrics(label, value):
    """Display a metric in a styled container"""
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)
