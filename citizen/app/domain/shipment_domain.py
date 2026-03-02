import uuid
from datetime import datetime


class Shipment:

    def __init__(
        self,
        order_id: str,
        shiprocket_order_id: int,
        shipment_id: int,
        awb_code: str,
        courier_name: str,
        tracking_url: str,
        current_status: str = "CREATED",
        id: str = None
    ):
        self.id = id or str(uuid.uuid4())
        self.order_id = order_id
        self.shiprocket_order_id = shiprocket_order_id
        self.shipment_id = shipment_id
        self.awb_code = awb_code
        self.courier_name = courier_name
        self.tracking_url = tracking_url
        self.current_status = current_status
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_status(self, status: str):
        self.current_status = status
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return self.__dict__