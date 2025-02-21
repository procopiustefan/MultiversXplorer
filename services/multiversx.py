import requests
from datetime import datetime

class MultiversXService:
    def __init__(self):
        self.base_url = "https://api.multiversx.com"

    def get_network_stats(self):
        """Fetch network statistics from MultiversX API"""
        try:
            response = requests.get(f"{self.base_url}/stats")
            print(f"Network stats response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()

            return {
                'transactions': data.get('transactions', 0),
                'active_addresses': data.get('accounts', 0),  # Changed from activeAddresses to accounts
                'tps': data.get('currentTps', 0),  # Added currentTps
                'staking_apr': 12.5  # Fixed value as it's not available in the stats endpoint
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching network stats: {str(e)}")
            return {
                'transactions': 0,
                'active_addresses': 0,
                'tps': 0,
                'staking_apr': 0
            }

    def get_recent_transactions(self):
        """Fetch recent transactions from MultiversX API"""
        try:
            response = requests.get(f"{self.base_url}/transactions?size=10")
            print(f"Recent transactions response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()

            transactions = []
            for tx in data:  # Removed .get('transactions', []) as the response is a direct array
                try:
                    transactions.append({
                        'hash': tx.get('txHash', ''),
                        'from': tx.get('sender', ''),
                        'to': tx.get('receiver', ''),
                        'amount': float(tx.get('value', 0)) / 1e18,
                        'timestamp': datetime.fromtimestamp(
                            int(tx.get('timestamp', 0))
                        ).strftime('%Y-%m-%d %H:%M:%S')
                    })
                except (ValueError, TypeError) as e:
                    print(f"Error processing transaction: {str(e)}")
                    continue

            return transactions
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transactions: {str(e)}")
            return []