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
    
    # shiprocket_client.py
    def get_courier_rates(self, order_id: str):
        self.ensure_token()
        url = f"{BASE_URL}/courier/serviceability?order_id={order_id}"
        
        response = requests.get(url, headers=self.headers())

        data = response.json()

        print("print courier list response - shiprocket_client.py:85",data)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch courier rates: {response.text}")
        
        return data
        
    # Assign courier
    def assign_courier(self, shipment_id: str, courier_id: int = None):
        """
        Assign a courier for a shipment.
        Returns a dictionary with AWB info if successful.
        """

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
        # data = {
        #     "awb_assign_status": 1,
        #     "response": {
        #         "data": {
        #             "courier_company_id": 54,
        #             "awb_code": "SRSP2269025472",
        #             "cod": 0,
        #             "order_id": 1216226902,
        #             "shipment_id": 1212533805,
        #             "awb_code_status": 1,
        #             "assigned_date_time": {
        #                 "date": "2026-03-05 13:03:42.000000",
        #                 "timezone_type": 3,
        #                 "timezone": "Asia/Kolkata"
        #             },
        #             "applied_weight": 0.5,
        #             "company_id": 9421320,
        #             "courier_name": "Ekart Logistics Surface",
        #             "child_courier_name": None,
        #             "freight_charges": 57,
        #             "routing_code": "", 
        #             "rto_routing_code": None,
        #             "invoice_no": "Retail00002",
        #             "transporter_id": "",
        #             "transporter_name": "",
        #             "shipped_by": {
        #                 "shipper_company_name": "rajesh",
        #                 "shipper_address_1": "s1, 2nd floor, sai akash apt",
        #                 "shipper_address_2": "near om sakthi temple",
        #                 "shipper_city": "Kanchipuram",
        #                 "shipper_state": "Tamil Nadu",
        #                 "shipper_country": "India",
        #                 "shipper_postcode": "600100",
        #                 "shipper_first_mile_activated": 0,
        #                 "shipper_phone": "9600296812",
        #                 "lat": "12.9171412",
        #                 "long": "80.1940972",
        #                 "shipper_email": "saravana.kumar@skylimitdigital.com",
        #                 "extra_info": {
        #                     "role": "Warehouse Manager",
        #                     "source": 1,
        #                     "open_time": "12:00 AM",
        #                     "close_time": "7:30 PM",
        #                     "select_days": '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]',
        #                     "alternate_name": "harish",
        #                     "alternate_role": "Warehouse Manager",
        #                     "alternate_email": "crazykidsri@gmail.com"
        #                 },
        #                 "rto_company_name": "rajesh",
        #                 "rto_address_1": "s1, 2nd floor, sai akash apt",
        #                 "rto_address_2": "near om sakthi temple",
        #                 "rto_city": "Kanchipuram",
        #                 "rto_state": "Tamil Nadu",
        #                 "rto_country": "India",
        #                 "rto_postcode": "600100",
        #                 "rto_phone": "9600296812",
        #                 "rto_email": "saravana.kumar@skylimitdigital.com"
        #             }
        #         }
        #     },
        #     "no_pickup_popup": 0,
        #     "quick_pick": 0
        # }
        print("Shiprocket assign courier response: - shiprocket_client.py:175", data)

        # Check if AWB was actually assigned
        awb_status = data.get("awb_assign_status")
        if awb_status == 1:
            # Successful assignment
            awb_data = data.get("response", {}).get("data", {})
            return {
                "awb_code": awb_data.get("awb_code"),
                "courier_name": awb_data.get("courier_name"),
                "freight_charges": awb_data.get("freight_charges"),
                "shipment_id": awb_data.get("shipment_id"),
                "order_id": awb_data.get("order_id"),
                "cod": awb_data.get("cod"),
                "raw_response": data
            }
        else:
            # Assignment failed
            raise Exception(f"Assign courier failed: {data}")

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
    def cancel_order(self, order_id: str):
        """
        Cancel an order in Shiprocket.
        Returns the full API response.
        """
        self.ensure_token()
        url = f"{BASE_URL}/orders/cancel"
        payload = {"ids": [order_id]}

        response = requests.post(url, headers={**self.headers(), "Content-Type": "application/json"}, json=payload)
        data = response.json()

        if response.status_code != 200 or data.get("status_code") not in [200, 201]:
            raise Exception(f"Cancel order failed: {data}")

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
            print("service availablity resp!!!!!!!!!!!!!!!!!!!!! - shiprocket_client.py:329",resp.json())
        except requests.RequestException as e:
            raise Exception(f"Shiprocket request failed: {str(e)}")

        # Debug logs
        print("Shiprocket serviceability response status: - shiprocket_client.py:334", resp.status_code)
        print("Request URL: - shiprocket_client.py:335", resp.url)

        try:
            data = resp.json()
        except ValueError:
            raise Exception(f"Invalid JSON response from Shiprocket: {resp.text}")

        if resp.status_code != 200:
            raise Exception(f"Failed to fetch courier list: {data}")

        return data

    # def get_couriers_by_address(
    #     self,
    #     pickup_postcode,
    #     delivery_postcode,
    #     weight,
    #     cod,
    #     declared_value,
    #     length=10,
    #     breadth=10,
    #     height=10
    # ):
    #     """
    #     Fetch available couriers using Shiprocket OPEN serviceability API
    #     (No auth required)
    #     """

    #     url = "https://serviceability.shiprocket.in/open/courier/serviceability"

    #     params = {
    #         "pickup_postcode": pickup_postcode,
    #         "delivery_postcode": delivery_postcode,
    #         "weight": 1,
    #         "cod": 1,
    #         "declared_value": declared_value,
    #         "length": length,
    #         "breadth": breadth,
    #         "height": height
    #     }

    #     # ✅ IMPORTANT: mimic browser headers
    #     headers = {
    #         "accept": "*/*",
    #         "origin": "https://www.shiprocket.in",
    #         "referer": "https://www.shiprocket.in/",
    #         "user-agent": "Mozilla/5.0"
    #     }

    #     try:
    #         resp = requests.get(url, headers=headers, params=params, timeout=10)
    #         print("service availablity resp!!!!!!!!!!!!!!!!!!!!!",resp.json())
    #     except requests.RequestException as e:
    #         raise Exception(f"Shiprocket request failed: {str(e)}")

    #     print("Status:", resp.status_code)
    #     print("URL:", resp.url)

    #     if resp.status_code != 200:
    #         raise Exception(f"Failed to fetch courier list: {resp.text}")

    #     try:
    #         data = resp.json()
    #     except ValueError:
    #         raise Exception(f"Invalid JSON response: {resp.text}")

    #     return data

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
        print("hyperlocal @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ cod or prepaid - shiprocket_client.py:420",cod)
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
            print("HYPERLOCAL RESPONSE: - shiprocket_client.py:434", resp)
            print("HYPERLOCAL RESPONSE: - shiprocket_client.py:435", resp.json())
        except requests.RequestException as e:
            raise Exception(f"Shiprocket request failed: {str(e)}")

        if resp.status_code != 200:
            raise Exception(f"Hyperlocal API failed: {resp.text}")

        return resp.json()