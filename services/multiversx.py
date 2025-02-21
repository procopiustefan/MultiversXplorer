import requests
from datetime import datetime

class MultiversXService:
    def __init__(self):
        self.base_url = "https://api.multiversx.com"
        
    def get_network_stats(self):
        """Fetch network statistics from MultiversX API"""
        try:
            response = requests.get(f"{self.base_url}/network/stats")
            data = response.json()
            
            return {
                'transactions': data.get('transactions', 0),
                'active_addresses': data.get('activeAddresses', 0),
                'tps': data.get('tps', 0),
                'staking_apr': data.get('stakingAPR', 0)
            }
        except Exception as e:
            print(f"Error fetching network stats: {e}")
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
            data = response.json()
            
            transactions = []
            for tx in data.get('transactions', []):
                transactions.append({
                    'hash': tx.get('txHash', ''),
                    'from': tx.get('sender', ''),
                    'to': tx.get('receiver', ''),
                    'amount': float(tx.get('value', 0)) / 1e18,
                    'timestamp': datetime.fromtimestamp(
                        int(tx.get('timestamp', 0))
                    ).strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return transactions
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []
