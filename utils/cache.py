import streamlit as st
from datetime import datetime, timedelta

def get_cached_data(key, fetch_func, ttl_minutes=5):
    """
    Fetch and cache data with TTL
    """
    # Create cache key with timestamp
    cache_key = f"{key}_data"
    timestamp_key = f"{key}_timestamp"
    
    # Check if data exists and is still valid
    if cache_key in st.session_state and timestamp_key in st.session_state:
        cached_time = st.session_state[timestamp_key]
        if datetime.now() - cached_time < timedelta(minutes=ttl_minutes):
            return st.session_state[cache_key]
    
    # Fetch new data
    data = fetch_func()
    
    # Update cache
    st.session_state[cache_key] = data
    st.session_state[timestamp_key] = datetime.now()
    
    return data
