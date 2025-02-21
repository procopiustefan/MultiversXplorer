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
                'active_addresses': data.get('accounts', 0),
                'tps': data.get('currentTps', 0),
                'staking_apr': 12.5
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching network stats: {str(e)}")
            return {
                'transactions': 0,
                'active_addresses': 0,
                'tps': 0,
                'staking_apr': 0
            }

    def get_staking_stats(self):
        """Fetch staking statistics from MultiversX API"""
        try:
            response = requests.get(f"{self.base_url}/stake")
            print(f"Staking stats response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()

            return {
                'total_validators': data.get('totalValidators', 0),
                'active_validators': data.get('activeValidators', 0),
                'total_observers': data.get('totalObservers', 0),
                'total_staked': float(data.get('totalStaked', 0)) / 1e18,  # Convert from wei to EGLD
                'nakamoto_coefficient': data.get('nakamotoIndex', 0)
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching staking stats: {str(e)}")
            return {
                'total_validators': 0,
                'active_validators': 0,
                'total_observers': 0,
                'total_staked': 0,
                'nakamoto_coefficient': 0
            }

    def get_recent_transactions(self):
        """Fetch recent transactions from MultiversX API"""
        try:
            response = requests.get(f"{self.base_url}/transactions?size=10")
            print(f"Recent transactions response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()

            transactions = []
            for tx in data:
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