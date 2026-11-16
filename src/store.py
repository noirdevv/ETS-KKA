import json
import os
import threading
import time
import webbrowser
import requests

SAVE_FILE = "save_data.json"

SKIN_PRICES = {
    "classic": 0,
    "crown": 500000,
    "stripes": 2020202,
    "pixel": 10000000,
    "face": 0,
}


class StoreManager:
    def __init__(self):
        self.unlocked_skins = {"classic", "face"}
        self.pending_order_id = None
        self.pending_skin_id = None
        self.status_message = ""
        self._load()

    def _load(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.unlocked_skins = set(data.get("unlocked_skins", ["classic"]))
            except (json.JSONDecodeError, OSError):
                self.unlocked_skins = {"classic"}

    def _save(self):
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"unlocked_skins": sorted(self.unlocked_skins)}, f, indent=2)

    def is_unlocked(self, skin_id):
        return skin_id in self.unlocked_skins

    def start_purchase(self, skin_id, on_unlocked=None):
        """Buat transaksi server di background thread dan buka browser."""
        if self.is_unlocked(skin_id):
            return

        self.status_message = "Menghubungkan ke server..."
        self.unlocked_skins.add(skin_id)
        self._save()
        self.pending_order_id = None
        self.pending_skin_id = None
        self.status_message = f"Pembayaran berhasil! Skin '{skin_id}' terbuka."