import os
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import json
import logging

class Database:
    def __init__(self):
        """Initialize database connection"""
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://multiversx_user:jm2bwE2KbUFRHX9erngeU4yptqQoTLX1@dpg-cuu90a56l47c73adgdvg-a/multiversx')
        self.engine = create_engine(self.db_url)
        self.create_tables()

    def create_tables(self):
        """Create necessary tables if they don't exist"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS wallet_data (
                    address TEXT PRIMARY KEY,
                    balance FLOAT,
                    transfers JSON,
                    daily_flows JSON,
                    last_updated TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS market_data (
                    price FLOAT,
                    volume_24h FLOAT,
                    market_cap FLOAT,
                    circulating_supply FLOAT,
                    last_updated TIMESTAMP PRIMARY KEY
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS network_stats (
                    transactions INTEGER,
                    active_addresses INTEGER,
                    tps FLOAT,
                    last_updated TIMESTAMP PRIMARY KEY
                )
            """))
            conn.commit()

    def update_wallet_data(self, address, data):
        """Store wallet data with timestamp"""
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO wallet_data 
                        (address, balance, transfers, daily_flows, last_updated)
                        VALUES (:address, :balance, :transfers, :daily_flows, :last_updated)
                        ON CONFLICT (address) 
                        DO UPDATE SET 
                            balance = :balance,
                            transfers = :transfers,
                            daily_flows = :daily_flows,
                            last_updated = :last_updated
                    """),
                    {
                        'address': address,
                        'balance': float(data['balance']),
                        'transfers': json.dumps(data['transfers']),
                        'daily_flows': json.dumps(data['daily_flows']),
                        'last_updated': datetime.now()
                    }
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Error updating wallet data: {e}")
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