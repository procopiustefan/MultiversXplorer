import sqlite3
from datetime import datetime, timedelta
import json
import os

class Database:
    def __init__(self):
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Connect to database
        self.conn = sqlite3.connect('data/multiversx.db')
        self.create_tables()

    def create_tables(self):
        """Create necessary tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Wallet balances and transactions
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS wallet_data (
            address TEXT,
            balance REAL,
            transfers TEXT,
            daily_flows TEXT,
            last_updated TIMESTAMP,
            PRIMARY KEY (address)
        )
        ''')

        # Market data
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_data (
            price REAL,
            volume_24h REAL,
            market_cap REAL,
            circulating_supply REAL,
            last_updated TIMESTAMP,
            PRIMARY KEY (last_updated)
        )
        ''')

        # Network stats
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS network_stats (
            transactions INTEGER,
            active_addresses INTEGER,
            tps REAL,
            last_updated TIMESTAMP,
            PRIMARY KEY (last_updated)
        )
        ''')

        self.conn.commit()

    def update_wallet_data(self, address, data):
        """Store wallet data with timestamp"""
        cursor = self.conn.cursor()
        
        try:
            # Convert datetime objects to ISO format strings in transfers
            transfers = []
            for transfer in data['transfers']:
                transfers.append({
                    'timestamp': transfer['timestamp'].isoformat(),
                    'value': float(transfer['value']),  # Ensure value is float
                    'action': transfer['action']
                })
            
            # Convert datetime objects to ISO format strings in daily_flows
            daily_flows = []
            for flow in data['daily_flows']:
                daily_flows.append({
                    'date': flow['date'].isoformat(),
                    'inflow': float(flow['inflow']),  # Ensure values are float
                    'outflow': float(flow['outflow']),
                    'net_flow': float(flow['net_flow'])
                })
            
            cursor.execute('''
            INSERT OR REPLACE INTO wallet_data 
            (address, balance, transfers, daily_flows, last_updated)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                address,
                float(data['balance']),  # Ensure balance is float
                json.dumps(transfers),
                json.dumps(daily_flows),
                datetime.now().isoformat()
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Error updating wallet data: {e}")
            raise

    def get_wallet_data(self, address, max_age_minutes=10):
        """Get wallet data if not too old"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT balance, transfers, daily_flows, last_updated
        FROM wallet_data
        WHERE address = ? AND last_updated > ?
        ''', (
            address,
            (datetime.now() - timedelta(minutes=max_age_minutes)).isoformat()
        ))
        
        row = cursor.fetchone()
        if row:
            # Convert ISO format strings back to datetime objects
            transfers = json.loads(row[1])
            for transfer in transfers:
                transfer['timestamp'] = datetime.fromisoformat(transfer['timestamp'])
            
            daily_flows = json.loads(row[2])
            for flow in daily_flows:
                flow['date'] = datetime.fromisoformat(flow['date'])
            
            return {
                'balance': row[0],
                'transfers': transfers,
                'daily_flows': daily_flows
            }
        return None

    def close(self):
        self.conn.close()

    def check_connection(self):
        """Check if database connection is working"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            print("Database connection successful!")
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def get_stats(self):
        """Get database statistics"""
        cursor = self.conn.cursor()
        stats = {}
        
        # Count records in each table
        cursor.execute("SELECT COUNT(*) FROM wallet_data")
        stats['wallet_records'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM market_data")
        stats['market_records'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM network_stats")
        stats['network_records'] = cursor.fetchone()[0]
        
        # Get last update times
        cursor.execute("SELECT MAX(last_updated) FROM wallet_data")
        stats['last_wallet_update'] = cursor.fetchone()[0]
        
        return stats 