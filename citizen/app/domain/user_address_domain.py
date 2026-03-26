class UserAddress:
    def __init__(
        self,
        user_id: str,
        address: str,
        first_name: str = None,
        last_name: str = None,
        landmark: str = None,
        city: str = None,
        state: str = None,
        country: str = None,
        postal_code: str = None,
        phone: str = None,
        email: str = None,
        is_default: bool = False,
        id: str = None,
        created_at=None,
        updated_at=None
    ):
        self.id = id
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.landmark = landmark
        self.city = city
        self.state = state
        self.country = country
        self.postal_code = postal_code
        self.phone = phone
        self.email = email
        self.is_default = is_default
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return self.__dict__