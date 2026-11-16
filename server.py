import base64
import hashlib
import os
import time
import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
load_dotenv()

MIDTRANS_SERVER_KEY = os.getenv("MIDTRANS_SERVER_KEY")
MIDTRANS_SNAP_URL = "https://app.sandbox.midtrans.com/snap/v1/transactions"

# Katalog harga dalam IDR
CATALOG = {
    "crown": {"name": "Skin Mahkota & Perisai", "price": 500000},
    "stripes": {"name": "Skin Garis & Polkadot", "price": 2020202},
    "pixel": {"name": "Skin Sprite PNG", "price": 10000000},
}

ORDERS = {}


class OrderRequest(BaseModel):
    skin_id: str
    player_name: str = "Player"


def _auth_header():
    token = base64.b64encode(f"{MIDTRANS_SERVER_KEY}:".encode()).decode()
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Basic {token}",
    }


@app.post("/create-order")
def create_order(req: OrderRequest):
    if req.skin_id not in CATALOG:
        raise HTTPException(status_code=400, detail="Skin tidak ditemukan")

    item = CATALOG[req.skin_id]
    order_id = f"GGS-{req.skin_id.upper()}-{int(time.time() * 1000)}"

    payload = {
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": item["price"],
        },
        "item_details": [
            {
                "id": req.skin_id,
                "price": item["price"],
                "quantity": 1,
                "name": item["name"],
            }
        ],
        "customer_details": {
            "first_name": req.player_name,
        },
    }

    resp = requests.post(MIDTRANS_SNAP_URL, json=payload, headers=_auth_header(), timeout=10)
    if resp.status_code not in (200, 201):
        resp = requests.post(MIDTRANS_SNAP_URL, json=payload, headers=_auth_header(), timeout=10)
        if resp.status_code not in (200, 201):
            print("MIDTRANS ERROR:", resp.status_code, resp.text)
            raise HTTPException(status_code=502, detail=f"Midtrans error: {resp.text}")
        raise HTTPException(status_code=502, detail=f"Midtrans error: {resp.text}")

    data = resp.json()
    ORDERS[order_id] = {"status": "pending", "skin_id": req.skin_id}
    return {
        "order_id": order_id,
        "redirect_url": data["redirect_url"],
    }


@app.post("/midtrans-webhook")
async def midtrans_webhook(request: Request):
    """Dipanggil otomatis oleh server Midtrans saat pembayaran selesai."""
    body = await request.json()
    order_id = body.get("order_id", "")
    status_code = body.get("status_code", "")
    gross_amount = body.get("gross_amount", "")
    signature_key = body.get("signature_key", "")

    # Verifikasi SHA-512 signature agar webhook palsu ditolak
    raw = f"{order_id}{status_code}{gross_amount}{MIDTRANS_SERVER_KEY}"
    expected_sig = hashlib.sha512(raw.encode()).hexdigest()
    if signature_key != expected_sig:
        raise HTTPException(status_code=403, detail="Invalid signature")

    tx_status = body.get("transaction_status")
    fraud_status = body.get("fraud_status", "accept")

    if order_id in ORDERS:
        if tx_status == "capture" and fraud_status == "accept":
            ORDERS[order_id]["status"] = "paid"
        elif tx_status == "settlement":
            ORDERS[order_id]["status"] = "paid"
        elif tx_status in ("deny", "cancel", "expire"):
            ORDERS[order_id]["status"] = "failed"

    return {"ok": True}


@app.get("/order-status/{order_id}")
def get_order_status(order_id: str):
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail="Order tidak ditemukan")
    return ORDERS[order_id]