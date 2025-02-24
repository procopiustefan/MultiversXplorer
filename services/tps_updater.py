import threading
import time
import requests
from datetime import datetime
import streamlit as st

class TPSUpdater:
    def __init__(self):
        self.base_url = "https://multiversx-api.blastapi.io/6016bb9c-17f6-43f4-aff4-890334b7f628"
        self.headers = {
            'Accept': 'application/json'
        }
        self.running = False
        self.thread = None
        self._current_tps = 0
        self._lock = threading.Lock()

    @property
    def current_tps(self):
        with self._lock:
            return self._current_tps

    def calculate_tps(self):
        try:
            blocks_response = requests.get(
                f"{self.base_url}/blocks?size=100",
                headers=self.headers
            )
            blocks_response.raise_for_status()
            blocks = blocks_response.json()

            if not blocks:
                return 0

            latest_blocks = {}
            for block in blocks:
                shard = block.get('shard', 0)
                if shard not in latest_blocks:
                    latest_blocks[shard] = block
                elif block.get('round', 0) > latest_blocks[shard].get('round', 0):
                    latest_blocks[shard] = block

            total_tx_count = 0
            total_time = 6  # seconds per round

            # Process regular shards (0,1,2)
            for shard in [0, 1, 2]:
                if shard in latest_blocks:
                    tx_count = latest_blocks[shard].get('txCount', 0)
                    total_tx_count += tx_count

            # Process metachain (4294967295)
            if 4294967295 in latest_blocks:
                meta_tx_count = latest_blocks[4294967295].get('txCount', 0)
                total_tx_count += meta_tx_count

            tps = total_tx_count / total_time if total_time > 0 else 0
            return round(tps, 2)

        except Exception:
            return 0

    def update_tps(self):
        while self.running:
            try:
                tps = self.calculate_tps()
                with self._lock:
                    self._current_tps = tps
                time.sleep(6)
            except Exception as e:
                print(f"Error updating TPS: {e}")
                time.sleep(6)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.update_tps, daemon=True)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join() 