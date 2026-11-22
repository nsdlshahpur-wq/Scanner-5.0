"""Minimal DhanHQ v2 client for Scanner 5.0.

Credentials are supplied per Streamlit session and are never written to disk.
Live orders are additionally gated by server-side static-IP deployment settings.
"""
from __future__ import annotations
import os
from typing import Any
import requests

BASE_URL = "https://api.dhan.co/v2"
TIMEOUT = 15

class DhanAPIError(RuntimeError):
    """Safe, user-displayable Dhan API error."""

class DhanClient:
    def __init__(self, client_id: str, access_token: str):
        self.client_id = client_id.strip()
        self.access_token = access_token.strip()
        if not self.client_id or not self.access_token:
            raise DhanAPIError("Dhan Client ID और Access Token दोनों आवश्यक हैं।")

    def _request(self, method: str, path: str, *, json_body: dict | None = None) -> Any:
        headers = {"access-token": self.access_token, "client-id": self.client_id,
                   "Accept": "application/json", "Content-Type": "application/json"}
        try:
            response = requests.request(method, f"{BASE_URL}{path}", headers=headers,
                                         json=json_body, timeout=TIMEOUT)
        except requests.RequestException:
            raise DhanAPIError("Dhan API से संपर्क नहीं हो सका। नेटवर्क/सर्वर जाँचें।") from None
        try:
            payload = response.json() if response.content else {}
        except ValueError:
            payload = {"message": "Dhan API ने पढ़ने योग्य JSON नहीं लौटाया।"}
        if not response.ok:
            message = payload.get("errorMessage") or payload.get("message") or f"HTTP {response.status_code}"
            raise DhanAPIError(str(message)[:300])
        return payload

    def profile(self) -> dict:
        return self._request("GET", "/profile")
    def funds(self) -> Any:
        return self._request("GET", "/fundlimit")
    def holdings(self) -> Any:
        return self._request("GET", "/holdings")
    def positions(self) -> Any:
        return self._request("GET", "/positions")
    def orders(self) -> Any:
        return self._request("GET", "/orders")

    def ltp(self, exchange_segment: str, security_id: str) -> dict:
        allowed = {"NSE_EQ", "BSE_EQ", "NSE_FNO", "BSE_FNO", "NSE_CURRENCY", "BSE_CURRENCY", "MCX_COMM"}
        if exchange_segment not in allowed:
            raise DhanAPIError("अमान्य Exchange Segment.")
        if not security_id.strip().isdigit():
            raise DhanAPIError("Security ID केवल अंकों में होना चाहिए।")
        return self._request("POST", "/marketfeed/ltp",
                             json_body={exchange_segment: [int(security_id)]})

    def place_order(self, *, transaction_type: str, exchange_segment: str,
                    product_type: str, order_type: str, validity: str,
                    security_id: str, quantity: int, price: float = 0.0,
                    trigger_price: float = 0.0) -> dict:
        if os.getenv("DHAN_ENABLE_LIVE_ORDERS", "").lower() != "true":
            raise DhanAPIError("Live Order अभी सर्वर पर बंद है। Static IP Whitelisting के बाद ही सक्षम करें।")
        if not os.getenv("DHAN_STATIC_IP", "").strip():
            raise DhanAPIError("DHAN_STATIC_IP सर्वर पर सेट नहीं है। Live Order रोका गया।")
        if transaction_type not in {"BUY", "SELL"}:
            raise DhanAPIError("अमान्य BUY/SELL विकल्प।")
        if exchange_segment not in {"NSE_EQ", "BSE_EQ", "NSE_FNO", "BSE_FNO", "MCX_COMM"}:
            raise DhanAPIError("अमान्य Exchange Segment.")
        if product_type not in {"CNC", "INTRADAY", "MARGIN", "MTF"}:
            raise DhanAPIError("अमान्य Product Type.")
        if order_type not in {"MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_MARKET"}:
            raise DhanAPIError("अमान्य Order Type.")
        if validity not in {"DAY", "IOC"}:
            raise DhanAPIError("अमान्य Order Validity.")
        if quantity < 1 or not security_id.strip().isdigit():
            raise DhanAPIError("Quantity या Security ID अमान्य है।")
        if order_type in {"LIMIT", "STOP_LOSS"} and price <= 0:
            raise DhanAPIError("इस Order Type के लिए Price आवश्यक है।")
        if order_type in {"STOP_LOSS", "STOP_LOSS_MARKET"} and trigger_price <= 0:
            raise DhanAPIError("Stop-loss Order के लिए Trigger Price आवश्यक है।")
        import uuid
        body = {
            "dhanClientId": self.client_id,
            "correlationId": "SCN" + uuid.uuid4().hex[:18],
            "transactionType": transaction_type,
            "exchangeSegment": exchange_segment,
            "productType": product_type,
            "orderType": order_type,
            "validity": validity,
            "securityId": security_id.strip(),
            "quantity": str(quantity),
            "price": str(price) if price > 0 else "",
            "triggerPrice": str(trigger_price) if trigger_price > 0 else "",
            "afterMarketOrder": False,
        }
        return self._request("POST", "/orders", json_body=body)

def live_orders_enabled() -> bool:
    return (os.getenv("DHAN_ENABLE_LIVE_ORDERS", "").lower() == "true"
            and bool(os.getenv("DHAN_STATIC_IP", "").strip()))
