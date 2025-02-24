import schedule
import time
from threading import Thread
from services.database import Database
from services.multiversx import MultiversXService
from services.coinmarketcap import CoinMarketCapService

def update_all_data():
    """Update all data in database"""
    db = Database()
    mx = MultiversXService()
    cmc = CoinMarketCapService()
    
    try:
        # Update wallet data
        wallets = {
            'binance': 'erd1sdslvlxvfnnflzj42l8czrcngq3xjjzkjp3rgul4ttk6hntr4qdsv6sets',
            'binance_cold': 'erd1v4ms58e22zjcp08suzqgm9ajmumwxcy4hfkdc23gvynnegjdflmsj6gmaq',
            'upbit': 'erd1hqamcl7hacu28q0l2kh7jt0vs6tjfhq4vp2tv7hufkx3phu0jn5ql3qw7x',
            'bybit': 'erd1vj3efd5czwearu0gr3vjct8ef53lvtl7vs42vts2kh2qn3cucrnsj7ymqx',
            'gateio': 'erd1p4vy5n9mlkdys7xczegj398xtyvw2nawz00nnfh4yr7fpjh297cqtsu7lw',
            'bitfinex': 'erd1a56dkgcpwwx6grmcvw9w5vpf9zeq53w3w7n6dmxcpxjry3l7uh2s3h9dtr',
            'cryptocom': 'erd1hzccjg25yqaqnr732x2ka7pj5glx72pfqzf05jj9hxqn3lxkramq5zu8h4',
            'kraken': 'erd1nmtkpqzhkla5yreu2dlyzm9fm8v902wjhvzu7xjjkd8ppefmtlws7qvx2a',
            'bitget': 'erd1w547kw69kpd60vlpr9pe0pn9nnqeljrcaz73znenjpgt0h3qlqqqm3szxj',
            'mexc': 'erd1ezp86jwmcp4fmmu2mfqz0438py392z5wp6kzuqsjldgd68nwt89qshfs0y',
            'coinbase': 'erd16jruked88jgtsar78ej85hjp3qsd9jkjcw4swsn7k0teqh3wgcqqgyrupq'
        }
        
        for name, address in wallets.items():
            data = mx.get_wallet_balance(address)
            db.update_wallet_data(f'{name}_wallet', data)
            time.sleep(1)  # Prevent rate limiting
            
        # Update other data types...
            
    finally:
        db.close()

def run_scheduler():
    """Run the scheduler in a separate thread"""
    schedule.every(10).minutes.do(update_all_data)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def start_updater():
    """Start the background updater thread"""
    thread = Thread(target=run_scheduler, daemon=True)
    thread.start()

def manual_update():
    """Manually trigger data update"""
    print("Starting manual data update...")
    update_all_data()
    print("Manual update completed!") 