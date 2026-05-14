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
        print("self.token - shiprocket_client.py:37",self.token)
        return {"Authorization": f"Bearer {self.token}"}

    # -----------------------
    # CREATE ORDER WITH STATIC ADDRESS
    # -----------------------
    def get_pickup_locations(self):
        self.ensure_token()
        url = f"{BASE_URL}/settings/company/pickup"
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
        print("Shiprocket create order response: - shiprocket_client.py:61", data)
        print("Shiprocket create order response: - shiprocket_client.py:62", data)
        print("Shipment ID: - shiprocket_client.py:63", data['shipment_id'])
        print("Order ID: - shiprocket_client.py:64", data['order_id'])
        print("AWB Code: - shiprocket_client.py:65", data['awb_code'])
        if response.status_code != 200:
            raise Exception(f"Shiprocket create order failed: {data}")

        # shipment_id = data.get("shipment_id") or data.get("data", {}).get("shipment_id")
        # print("shipment_id!!!!!!!!!!!!!!! - shiprocket_client.py:69",shipment_id)
        # if not shipment_id:
        #     raise Exception(f"No shipment_id returned from Shiprocket: {data}")

        return data  # return the full response, not just shipment_id
    

    def create_hyperlocal_order(self, payload: dict):
        self.ensure_token()

        response = requests.post(
            f"{BASE_URL}/orders/create/adhoc",
            headers={**self.headers(), "Content-Type": "application/json"},
            json=payload
        )

        data = response.json()

        print("Hyperlocal create response: - shiprocket_client.py:88", data)

        if response.status_code != 200:
            raise Exception(f"Hyperlocal create failed: {data}")

        # Hyperlocal response is different — safe extraction
        order_id = data.get("order_id") or data.get("data", {}).get("order_id")
        tracking_url = data.get("tracking_url") or data.get("data", {}).get("tracking_url")
        courier_name = data.get("courier_name") or data.get("data", {}).get("courier_name")

        print("Hyperlocal Order ID: - shiprocket_client.py:98", order_id)
        print("Tracking URL: - shiprocket_client.py:99", tracking_url)
        print("Courier Name: - shiprocket_client.py:100", courier_name)

        return data
    
    # shiprocket_client.py
    def get_courier_rates(self, order_id: str):
        self.ensure_token()
        url = f"{BASE_URL}/courier/serviceability?order_id={order_id}"
        
        response = requests.get(url, headers=self.headers())

        data = response.json()

        print("print courier list response - shiprocket_client.py:113",data)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch courier rates: {response.text}")
        
        return data
        
    # Assign courier
    def assign_courier(self, shipment_id: str, courier_id: int = None):
        """
        Assign a courier for a shipment.
        Never throws exception for business-level failures.
        """

        self.ensure_token()

        payload = {"shipment_id": shipment_id}
        if courier_id is not None:
            payload["courier_id"] = courier_id

        try:
            response = requests.post(
                f"{BASE_URL}/courier/assign/awb",
                headers={**self.headers(), "Content-Type": "application/json"},
                json=payload,
                timeout=20
            )

            data = response.json()
            print("Shiprocket assign courier response: - shiprocket_client.py:142", data)

        except Exception as e:
            return {
                "success": False,
                "message": f"Request failed: {str(e)}",
                "awb_code": None
            }

        # -----------------------------
        # SUCCESS CASE
        # -----------------------------
        if data.get("awb_assign_status") == 1:
            awb_data = (data.get("response") or {}).get("data") or {}

            return {
                "success": True,
                "awb_code": awb_data.get("awb_code"),
                "courier_name": awb_data.get("courier_name"),
                "freight_charges": awb_data.get("freight_charges"),
                "shipment_id": awb_data.get("shipment_id"),
                "order_id": awb_data.get("order_id"),
                "cod": awb_data.get("cod"),
                "raw_response": data
            }

        # -----------------------------
        # FAILURE CASE (IMPORTANT FIX)
        # -----------------------------
        return {
            "success": False,
            "message": (
                data.get("response", {}).get("data")
                or "Courier not available for AWB assignment"
            ),
            "awb_code": None,
            "raw_response": data
        }
    

    def hyper_local_assign_courier(self, shipment_id: int, courier_id=None):

        self.ensure_token()

        payload = {
            "shipment_id": int(shipment_id)
        }

        # -----------------------------
        # courier_id is OPTIONAL in hyperlocal
        # -----------------------------
        if courier_id not in [None, "", 0, "0"]:
            try:
                payload["courier_id"] = int(courier_id)
            except Exception:
                return {
                    "success": False,
                    "status": "invalid_input",
                    "message": "Invalid courier_id",
                    "awb_code": None
                }

        try:
            response = requests.post(
                f"{BASE_URL}/courier/assign/awb",
                headers={**self.headers(), "Content-Type": "application/json"},
                json=payload,
                timeout=20
            )

            data = response.json()
            print("Hyperlocal assign response: - shiprocket_client.py:213", data)

        except Exception as e:
            return {
                "success": False,
                "status": "request_failed",
                "message": str(e),
                "awb_code": None
            }

        # -----------------------------
        # CASE 1: IMMEDIATE AWB (RARE)
        # -----------------------------
        if data.get("awb_assign_status") == 1:
            awb_data = (data.get("response") or {}).get("data") or {}

            return {
                "success": True,
                "status": "assigned",
                "processing": False,
                "awb_code": awb_data.get("awb_code"),
                "courier_name": awb_data.get("courier_name"),
                "raw_response": data
            }

        # -----------------------------
        # CASE 2: HYPERLOCAL PROCESSING / QUEUED
        # -----------------------------
        message = (
            data.get("message")
            or (data.get("response") or {}).get("data")
            or ""
        )

        if (
            "processing" in message.lower()
            or "try later" in message.lower()
            or data.get("awb_assign_status") == 0
        ):
            return {
                "success": True,
                "status": "processing",
                "processing": True,
                "message": message,
                "awb_code": None,
                "courier_name": None,
                "raw_response": data
            }

        # -----------------------------
        # CASE 3: ACTUAL FAILURE
        # -----------------------------
        return {
            "success": False,
            "status": "failed",
            "message": message or "Hyperlocal courier assignment failed",
            "awb_code": None,
            "raw_response": data
        }


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
    
    def download_label(self, shipment_id: str):
        """
        Generate & download the PDF label for a shipment.
        Returns the label URL.
        """
        self.ensure_token()

        # 1️⃣ Generate label first
        try:
            generate_response = self.generate_label(shipment_id)
        except Exception as e:
            raise Exception(f"Failed to generate label: {str(e)}")

        # 2️⃣ Extract file URL
        label_url = generate_response.get("label_url") or generate_response.get("data", {}).get("label_url")
        if not label_url:
            raise Exception(f"No label URL returned: {generate_response}")

        return label_url

    # -----------------------
    # CANCEL ORDER
    # -----------------------
    def cancel_order(self, awb: str):
        """
        Cancel shipment using AWB (Shiprocket correct flow)
        """
        self.ensure_token()

        url = f"{BASE_URL}/orders/cancel/shipment/awbs"

        payload = {
            "awbs": [awb]
        }

        response = requests.post(
            url,
            headers={
                **self.headers(),
                "Content-Type": "application/json"
            },
            json=payload
        )

        data = response.json()

        if response.status_code not in [200, 201]:
            raise Exception(f"Cancel shipment failed: {data}")

        return data

    # -----------------------
    # REFUND ORDER
    # -----------------------
    def refund_order(self, order_id: str, amount: float):
        """
        Refund an order via Shiprocket.
        amount: float - refund amount
        Returns the full API response.
        """
        self.ensure_token()
        url = f"{BASE_URL}/orders/refund"
        payload = {
            "order_id": order_id,
            "amount": amount
        }

        response = requests.post(url, headers={**self.headers(), "Content-Type": "application/json"}, json=payload)
        data = response.json()

        if response.status_code != 200 or data.get("status_code") not in [200, 201]:
            raise Exception(f"Refund order failed: {data}")

        return data
    
    def get_tracking(self, awb_code: str):
        """
        Get tracking details using AWB code
        """
        self.ensure_token()

        url = f"{BASE_URL}/courier/track/awb/{awb_code}"

        response = requests.get(url, headers=self.headers())

        if response.status_code != 200:
            raise Exception(f"Tracking fetch failed: {response.text}")

        return response.json()
    
    # shiprocket_client.py
    def get_couriers_by_address(
        self, pickup_postcode, delivery_postcode, weight, cod, declared_value, length, breadth, height
    ):
        """
        Fetch available couriers and rates for a shipment using Shiprocket serviceability API.
        
        Parameters:
        - pickup_postcode: str
        - delivery_postcode: str
        - weight: float (in kg)
        - cod: int (0 or 1)
        - declared_value: float
        - length, breadth, height: int (dimensions in cm, default 10)

        Returns:
        - dict: Shiprocket API response containing available couriers and rates.
        """
        # Ensure valid auth token
        self.ensure_token()

        url = f"{BASE_URL}/courier/serviceability"
        params = {
            "pickup_postcode": pickup_postcode,
            "delivery_postcode": delivery_postcode,
            "weight": weight,
            "cod": cod,
            "declared_value": declared_value,
            "length": length,
            "breadth": breadth,
            "height": height
        }

        try:
            # Corrected headers call
            resp = requests.get(url, headers=self.headers(), params=params)
            print("service availablity resp!!!!!!!!!!!!!!!!!!!!! - shiprocket_client.py:419",resp.json())
        except requests.RequestException as e:
            raise Exception(f"Shiprocket request failed: {str(e)}")

        # Debug logs
        print("Shiprocket serviceability response status: - shiprocket_client.py:424", resp.status_code)
        print("Request URL: - shiprocket_client.py:425", resp.url)

        try:
            data = resp.json()
        except ValueError:
            raise Exception(f"Invalid JSON response from Shiprocket: {resp.text}")

        if resp.status_code != 200:
            raise Exception(f"Failed to fetch courier list: {data}")

        return data

    def get_hyperlocal_couriers(
        self,
        pickup_postcode,
        delivery_postcode,
        lat_from,
        long_from,
        lat_to,
        long_to,
        cod
    ):
        """
        Fetch hyperlocal courier availability from Shiprocket
        """

        self.ensure_token()

        url = f"{BASE_URL}/courier/serviceability"
        print("hyperlocal @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ cod or prepaid - shiprocket_client.py:454",cod)
        params = {
            "pickup_postcode": pickup_postcode,
            "delivery_postcode": delivery_postcode,
            "cod": cod,
            "is_new_hyperlocal": 1,   # 🔥 IMPORTANT
            "lat_from": lat_from,
            "long_from": long_from,
            "lat_to": lat_to,
            "long_to": long_to
        }

        try:
            resp = requests.get(url, headers=self.headers(), params=params)
            print("HYPERLOCAL RESPONSE: - shiprocket_client.py:468", resp)
            print("HYPERLOCAL RESPONSE: - shiprocket_client.py:469", resp.json())
        except requests.RequestException as e:
            raise Exception(f"Shiprocket request failed: {str(e)}")

        if resp.status_code != 200:
            raise Exception(f"Hyperlocal API failed: {resp.text}")

        return resp.json()
    
    def get_wallet_balance(self):
        """
        Fetch Shiprocket wallet balance
        """
        self.ensure_token()

        url = f"{BASE_URL}/account/details/wallet-balance"

        response = requests.get(
            url,
            headers={**self.headers(), "Content-Type": "application/json"}
        )

        try:
            data = response.json()
        except Exception:
            raise Exception(f"Invalid JSON response: {response.text}")

        print("Wallet Balance Response: - shiprocket_client.py:496", data)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch wallet balance: {data}")

        return data
    
    def generate_manifest(self, shipment_ids: list):
        """
        Generate manifest for one or multiple shipments.
        Required before pickup handover in Shiprocket.
        """

        self.ensure_token()

        url = f"{BASE_URL}/manifests/generate"

        payload = {
            "shipment_id": shipment_ids
        }

        response = requests.post(
            url,
            headers={**self.headers(), "Content-Type": "application/json"},
            json=payload
        )

        try:
            data = response.json()
        except Exception:
            raise Exception(f"Invalid JSON response: {response.text}")

        print("Manifest Response: - shiprocket_client.py:528", data)

        if response.status_code != 200:
            raise Exception(f"Manifest generation failed: {data}")

        return data
    
    def generate_invoice(self, shipment_ids: list):

        self.ensure_token()

        url = f"{BASE_URL}/orders/print/invoice"

        payload = {
            "ids": [str(i) for i in shipment_ids]
        }

        response = requests.post(
            url,
            headers={**self.headers(), "Content-Type": "application/json"},
            json=payload
        )

        try:
            data = response.json()
        except Exception:
            raise Exception(f"Invalid Shiprocket response: {response.text}")

        print("Invoice response: - shiprocket_client.py:556", data)

        if response.status_code != 200:
            raise Exception(f"Invoice generation failed: {data}")

        return data
    
    # ---------------------------------------------------------
    # Generate Pickup
    # ---------------------------------------------------------
    def generate_pickup(self, shipment_ids: list):

        self.ensure_token()

        payload = {
            "shipment_id": shipment_ids
        }

        response = requests.post(
            f"{BASE_URL}/courier/generate/pickup",
            headers={
                **self.headers(),
                "Content-Type": "application/json"
            },
            json=payload
        )

        data = response.json()

        print("Generate pickup response: - shiprocket_client.py:585", data)

        if response.status_code != 200:
            raise Exception(
                f"Pickup generation failed: {data}"
            )

        return data