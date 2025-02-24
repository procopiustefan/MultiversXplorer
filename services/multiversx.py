import requests
from datetime import datetime, timedelta
import logging
import time
import streamlit as st

class MultiversXService:
    def __init__(self):
        self.base_url = "https://multiversx-api.blastapi.io/6016bb9c-17f6-43f4-aff4-890334b7f628"
        self.headers = {
            'Accept': 'application/json'
        }

    def get_network_stats(self):
        """Fetch network statistics from MultiversX API"""
        try:
            # Get network stats
            stats_response = requests.get(
                f"{self.base_url}/stats",
                headers=self.headers
            )
            stats_response.raise_for_status()
            stats = stats_response.json()

            # Get TPS from the updater if it exists in session state
            tps = 0
            if 'tps_updater' in st.session_state:
                tps = st.session_state.tps_updater.current_tps

            return {
                'transactions': stats.get('transactions', 0),
                'active_addresses': stats.get('accounts', 0),
                'tps': tps,
                'shards': {
                    'regular': [0, 1, 2],
                    'meta': 4294967295
                }
            }
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching network stats: {str(e)}")
            return {
                'transactions': 0,
                'active_addresses': 0,
                'tps': 0,
                'shards': {
                    'regular': [0, 1, 2],
                    'meta': 4294967295
                }
            }

    def get_staking_stats(self):
        """Fetch staking and economics statistics from MultiversX API"""
        try:
            stake_response = requests.get("https://api.multiversx.com/stake")
            stake_data = stake_response.json()
            
            econ_response = requests.get(f"{self.base_url}/economics")
            econ_data = econ_response.json()
            
            delegation_response = requests.get("https://api.multiversx.com/delegation-legacy")
            delegation_data = delegation_response.json()
            
            return {
                'total_validators': stake_data.get('totalValidators', 0),
                'active_validators': stake_data.get('activeValidators', 0),
                'total_observers': stake_data.get('totalObservers', 0),
                'nakamoto_coefficient': stake_data.get('nakamotoCoefficient', 9),
                'eligible_validators': stake_data.get('eligibleValidators', 0),
                'waiting_validators': stake_data.get('waitingValidators', 0),
                'total_staked': float(econ_data.get('staked', 0)),
                'staking_apr': float(econ_data.get('apr', 0)) * 100,
                'total_active_stake': float(delegation_data.get('totalActiveStake', '0')) / 1e18,
                'total_waiting_stake': float(delegation_data.get('totalWaitingStake', '0')) / 1e18,
                'total_unstaked': float(delegation_data.get('totalUnstakedStake', '0')) / 1e18,
                'total_deferred': float(delegation_data.get('totalDeferredPaymentStake', '0')) / 1e18,
                'total_withdraw': float(delegation_data.get('totalWithdrawOnlyStake', '0')) / 1e18,
                'staking_users': int(delegation_data.get('numUsers', 0))
            }
        except Exception as e:
            print(f"Error fetching staking/economics stats: {str(e)}")
            return {
                'total_validators': 0,
                'active_validators': 0,
                'total_observers': 0,
                'total_staked': 0,
                'nakamoto_coefficient': 0,
                'staking_apr': 0,
                'total_supply': 0,
                'circulating_supply': 0,
                'market_cap': 0,
                'total_active_stake': 0,
                'total_waiting_stake': 0,
                'total_unstaked': 0,
                'total_deferred': 0,
                'total_withdraw': 0,
                'staking_users': 0
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

    def get_wallet_balance(self, address):
        """Get wallet balance and transaction history for the last 30 days."""
        try:
            # Get current balance
            balance_response = requests.get(
                f"{self.base_url}/accounts/{address}",
                headers=self.headers
            )
            balance_response.raise_for_status()
            balance_data = balance_response.json()
            
            balance = float(balance_data.get('balance', 0)) / 10**18

            # Get transfers for last 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            
            # Fetch transfers with order=desc to get most recent first
            response = requests.get(
                f"{self.base_url}/accounts/{address}/transactions?size=9000&order=desc",
                headers=self.headers
            )
            
            response.raise_for_status()
            transactions = response.json()
            
            # Process transactions
            transfers = []
            for tx in transactions:
                timestamp = datetime.fromtimestamp(int(tx.get('timestamp', 0)))
                if timestamp < cutoff_date:
                    continue
                    
                value = float(tx.get('value', 0)) / 10**18
                transfers.append({
                    'timestamp': timestamp,
                    'value': value,
                    'action': 'outgoing' if tx.get('sender') == address else 'incoming'
                })

            # Sort transfers by timestamp
            transfers.sort(key=lambda x: x['timestamp'])

            # Calculate daily flows
            daily_flows = {}
            for transfer in transfers:
                date_key = transfer['timestamp'].strftime('%Y-%m-%d')
                if date_key not in daily_flows:
                    daily_flows[date_key] = {
                        'date': transfer['timestamp'].replace(hour=0, minute=0, second=0, microsecond=0),
                        'inflow': 0,
                        'outflow': 0,
                        'net_flow': 0
                    }
                
                if transfer['action'] == 'incoming':
                    daily_flows[date_key]['inflow'] += transfer['value']
                else:
                    daily_flows[date_key]['outflow'] += transfer['value']
                
                daily_flows[date_key]['net_flow'] = (
                    daily_flows[date_key]['inflow'] - daily_flows[date_key]['outflow']
                )

            # Convert daily flows to list and sort by date
            daily_flows_list = sorted(
                daily_flows.values(),
                key=lambda x: x['date']
            )

            return {
                'balance': balance,
                'transfers': transfers,
                'daily_flows': daily_flows_list
            }

        except Exception as e:
            logging.error(f"Error fetching wallet data: {str(e)}")
            return {
                'balance': 0,
                'transfers': [],
                'daily_flows': []
            }

    def get_staking_identities(self):
        """Fetch and categorize staking identities"""
        try:
            response = requests.get(
                f"{self.base_url}/identities",
                headers=self.headers
            )
            response.raise_for_status()
            identities = response.json()

            active_providers = 0
            inactive_providers = 0
            standalone_nodes = 0

            for identity in identities:
                stake = float(identity.get('stake', '0'))
                locked = float(identity.get('locked', '0'))
                
                # Check if it's a staking provider
                is_provider = ('providers' in identity or (
                    'distribution' in identity and 
                    any(key != 'direct' for key in identity['distribution'].keys())
                ))
                
                if is_provider:
                    if stake > 0 and locked > 0:
                        active_providers += 1
                    else:
                        inactive_providers += 1
                elif stake > 0:  # Standalone node with stake
                    standalone_nodes += 1

            return {
                'staking_providers': active_providers,
                'inactive_providers': inactive_providers,
                'standalone_nodes': standalone_nodes,
                'total_nodes': active_providers + standalone_nodes
            }
        except Exception as e:
            print(f"Error fetching staking identities: {e}")
            return {
                'staking_providers': 0,
                'inactive_providers': 0,
                'standalone_nodes': 0,
                'total_nodes': 0
            }