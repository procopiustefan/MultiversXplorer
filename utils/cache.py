import streamlit as st
from datetime import datetime, timedelta
from services.database import Database

def get_cached_data(key, fetch_func, ttl_minutes=10):
    """Get data from database cache or fetch fresh data"""
    db = Database()
    
    try:
        # For network stats, use shorter TTL
        if key == 'network_stats':
            ttl_minutes = 0.1  # 6 seconds
            
        # Try to get from cache first
        if 'wallet' in key:
            cached_data = db.get_wallet_data(key, ttl_minutes)
            if cached_data and cached_data['balance'] > 0:  # Only use cache if balance exists
                return cached_data
        
        # If not in cache or too old, fetch fresh data
        fresh_data = fetch_func()
        
        # Store in cache if it's wallet data
        if 'wallet' in key and fresh_data and fresh_data['balance'] > 0:
            db.update_wallet_data(key, fresh_data)
            
        return fresh_data
        
    except Exception as e:
        print(f"Cache error for {key}: {e}")
        return fetch_func()  # Fallback to fresh data
    finally:
        db.close()
