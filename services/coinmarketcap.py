import requests
import os
from datetime import datetime, timedelta
import random  # For generating sample data

class CoinMarketCapService:
    def __init__(self):
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
        self.egld_id = "6892"  # MultiversX ID on CMC
        api_key = os.getenv('COINMARKETCAP_API_KEY')
        if not api_key:
            print("Warning: COINMARKETCAP_API_KEY not found in environment variables")
        self.headers = {
            'X-CMC_PRO_API_KEY': api_key,
            'Accept': 'application/json'
        }

    def get_market_data(self):
        """Fetch current market data for EGLD"""
        try:
            response = requests.get(
                f"{self.base_url}/cryptocurrency/quotes/latest",
                params={'id': self.egld_id},
                headers=self.headers
            )
            print(f"Market data response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()

            if 'data' not in data:
                print(f"Unexpected API response structure: {data}")
                raise ValueError(f"Unexpected API response: {data}")

            quote = data['data'][self.egld_id]['quote']['USD']
            return {
                'price': round(quote['price'], 2),
                'volume_24h': quote['volume_24h'],
                'market_cap': quote['market_cap'],
                'percent_change_24h': round(quote['percent_change_24h'], 2),
                'circulating_supply': data['data'][self.egld_id]['circulating_supply']
            }
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {str(e)}")
            return self._get_default_market_data()
        except (KeyError, ValueError) as e:
            print(f"Error parsing market data: {str(e)}")
            return self._get_default_market_data()

    def get_historical_data(self, timeframe):
        """Fetch historical price data"""
        try:
            days = {
                '24h': 1,
                '7d': 7,
                '30d': 30,
                '90d': 90
            }[timeframe]

            # For 24h data, use hourly intervals
            if days == 1:
                interval = '1h'
                count = 24
            else:
                interval = '1d'
                count = days

            print(f"Fetching historical data for {days} days with {interval} interval")
            response = requests.get(
                f"{self.base_url}/cryptocurrency/quotes/historical",
                params={
                    'id': self.egld_id,
                    'interval': interval,
                    'count': count,
                    'convert': 'USD'
                },
                headers=self.headers
            )
            print(f"Historical data response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()

            if 'data' not in data:
                print(f"Unexpected historical data response: {data}")
                return self._get_sample_historical_data(days)

            return data['data']['quotes']
        except Exception as e:
            print(f"Error fetching historical data: {str(e)}")
            return self._get_sample_historical_data(days)

    def get_exchange_volumes(self):
        """Fetch exchange volume breakdown"""
        try:
            print("Fetching exchange volumes data")
            response = requests.get(
                f"{self.base_url}/cryptocurrency/market-pairs/latest",
                params={'id': self.egld_id, 'convert': 'USD'},
                headers=self.headers
            )
            print(f"Exchange volumes response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()

            if 'data' not in data:
                print(f"Unexpected exchange volume response: {data}")
                return self._get_sample_exchange_data()

            return data['data']['market_pairs']
        except Exception as e:
            print(f"Error fetching exchange volumes: {str(e)}")
            return self._get_sample_exchange_data()

    def _get_default_market_data(self):
        """Return sample market data for development"""
        return {
            'price': 35.42,  # Sample EGLD price
            'volume_24h': 15000000,  # Sample 24h volume
            'market_cap': 900000000,  # Sample market cap
            'percent_change_24h': 2.5,  # Sample 24h change
            'circulating_supply': 25000000  # Sample circulating supply
        }

    def _get_sample_historical_data(self, days):
        """Generate sample historical data with realistic price movements"""
        data = []
        base_time = datetime.now() - timedelta(days=days)
        base_price = 35.42  # Starting price
        last_price = base_price

        for i in range(days * 24 if days == 1 else days):
            # Generate realistic price movements
            price_change = random.uniform(-0.5, 0.5)  # Random price change
            new_price = last_price * (1 + price_change/100)  # Apply percentage change
            last_price = new_price

            # Generate realistic volume
            volume = random.uniform(10000000, 20000000)  # Random volume between 10M and 20M

            delta = timedelta(hours=i) if days == 1 else timedelta(days=i)
            timestamp = base_time + delta
            data.append({
                'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'quote': {
                    'USD': {
                        'price': round(new_price, 2),
                        'volume_24h': volume,
                    }
                }
            })

        return data

    def _get_sample_exchange_data(self):
        """Generate sample exchange data with realistic volumes"""
        exchanges = [
            ('Binance', 8000000),
            ('KuCoin', 4000000),
            ('Gate.io', 2500000),
            ('Huobi', 2000000),
            ('OKX', 1500000)
        ]
        data = []

        for exchange, base_volume in exchanges:
            # Add some randomness to volumes
            volume = base_volume * random.uniform(0.8, 1.2)
            data.append({
                'exchange': {'name': exchange},
                'quote': {'USD': {'volume_24h': volume}}
            })

        return data