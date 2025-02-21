import requests
from datetime import datetime, timedelta

class CoinMarketCapService:
    def __init__(self):
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
        self.egld_id = "6892"  # MultiversX ID on CMC
        
    def get_market_data(self):
        """Fetch current market data for EGLD"""
        try:
            response = requests.get(
                f"{self.base_url}/cryptocurrency/quotes/latest",
                params={'id': self.egld_id},
                headers={'X-CMC_PRO_API_KEY': 'YOUR_API_KEY'}
            )
            data = response.json()
            quote = data['data'][self.egld_id]['quote']['USD']
            
            return {
                'price': quote['price'],
                'volume_24h': quote['volume_24h'],
                'market_cap': quote['market_cap'],
                'circulating_supply': data['data'][self.egld_id]['circulating_supply']
            }
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return {
                'price': 0,
                'volume_24h': 0,
                'market_cap': 0,
                'circulating_supply': 0
            }

    def get_historical_data(self, timeframe):
        """Fetch historical price data"""
        try:
            days = {
                '24h': 1,
                '7d': 7,
                '30d': 30,
                '90d': 90
            }[timeframe]
            
            response = requests.get(
                f"{self.base_url}/cryptocurrency/quotes/historical",
                params={
                    'id': self.egld_id,
                    'interval': '1h' if days == 1 else '1d',
                    'count': days
                },
                headers={'X-CMC_PRO_API_KEY': 'YOUR_API_KEY'}
            )
            
            return response.json()['data']['quotes']
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return []

    def get_exchange_volumes(self):
        """Fetch exchange volume breakdown"""
        try:
            response = requests.get(
                f"{self.base_url}/cryptocurrency/market-pairs/latest",
                params={'id': self.egld_id},
                headers={'X-CMC_PRO_API_KEY': 'YOUR_API_KEY'}
            )
            
            return response.json()['data']['market_pairs']
        except Exception as e:
            print(f"Error fetching exchange volumes: {e}")
            return []
