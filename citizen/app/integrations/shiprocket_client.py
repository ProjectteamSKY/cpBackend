# shiprocket_client.py

import requests
from datetime import datetime, timedelta
from app.core.config import settings

BASE_URL = "https://apiv2.shiprocket.in/v1/external"


class ShiprocketClient:

    def __init__(self):
        self.token = None
        self.expiry = None

    # Authentication
    def authenticate(self):
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": settings.SHIPROCKET_EMAIL,
                "password": settings.SHIPROCKET_PASSWORD
            }
        )

        if response.status_code != 200:
            raise Exception(f"Shiprocket Authentication Failed: {response.text}")

        self.token = response.json()["token"]
        self.expiry = datetime.now() + timedelta(days=9)

    def ensure_token(self):
        if not self.token or datetime.now() >= self.expiry:
            self.authenticate()

    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    # -----------------------
    # CREATE ORDER WITH STATIC ADDRESS
    # -----------------------
    def get_pickup_locations(self):
        self.ensure_token()
        url = f"{BASE_URL}/settings/company/pickup-location"
        response = requests.get(url, headers=self.headers())
        if response.status_code != 200:
            raise Exception(f"Failed to fetch pickup locations: {response.text}")
        return response.json()

    def create_order(self, payload: dict):
        self.ensure_token()

        response = requests.post(
            f"{BASE_URL}/orders/create/adhoc",
            headers={**self.headers(), "Content-Type": "application/json"},
            json=payload
        )

        data = response.json()
        print("Shiprocket create order response: - shiprocket_client.py:60", data)
        print("Shiprocket create order response: - shiprocket_client.py:61", data)
        print("Shipment ID: - shiprocket_client.py:62", data['shipment_id'])
        print("Order ID: - shiprocket_client.py:63", data['order_id'])
        print("AWB Code: - shiprocket_client.py:64", data['awb_code'])
        if response.status_code != 200:
            raise Exception(f"Shiprocket create order failed: {data}")

        # shipment_id = data.get("shipment_id") or data.get("data", {}).get("shipment_id")
        # print("shipment_id!!!!!!!!!!!!!!! - shiprocket_client.py:69",shipment_id)
        # if not shipment_id:
        #     raise Exception(f"No shipment_id returned from Shiprocket: {data}")

        return data  # return the full response, not just shipment_id
    
    # shiprocket_client.py
    def get_courier_rates(self, order_id: str):
        self.ensure_token()
        url = f"{BASE_URL}/courier/serviceability?order_id={order_id}"
        
        response = requests.get(url, headers=self.headers())

        data = response.json()

        print("print courier list response - shiprocket_client.py:84",data)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch courier rates: {response.text}")
        
        return data
        
    # Assign courier
    def assign_courier(self, shipment_id: str, courier_id: int = None):
        self.ensure_token()
        
        payload = {"shipment_id": shipment_id}
        if courier_id is not None:
            payload["courier_id"] = courier_id  # include courier_id if provided

        response = requests.post(
            f"{BASE_URL}/courier/assign/awb",
            headers={**self.headers(), "Content-Type": "application/json"},
            json=payload
        )

        data = response.json()
        print("data assign courier - shiprocket_client.py:106",data)
        if response.status_code != 200 or data.get("status_code") not in [200, 201]:
            raise Exception(f"Assign courier failed: {data}")
        return data

    # Generate shipping label
    def generate_label(self, shipment_id: str):
        url = f"{BASE_URL}/courier/generate/label"
        response = requests.post(
            url,
            json={"shipment_id": [shipment_id]},
            headers={**self.headers(), "Content-Type": "application/json"}
        )
        if response.status_code != 200:
            raise Exception(f"Failed to generate label: {response.text}")
        return response.json()

    # Download PDF label
    def download_file(self, file_url: str):
        response = requests.get(file_url)
        if response.status_code != 200:
            raise Exception(f"Failed to download label: {response.status_code}")
        return response.content