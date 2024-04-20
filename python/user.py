from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass()
class User:
    uuid: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    active_subscription: float
    #https://stackoverflow.com/questions/68874635/why-is-my-python-dataclass-not-initialising-boolean-correctly
    inside_facility: Optional[bool] = field(default=False)

    def __str__(self) -> str:
        return f"uuid: {self.uuid}, is inside: {self.inside_facility}"
    
    """
    Check if the current User's subscription expiry date is larger than the current date.
    If it is, they have a valid subscription, so return true. Otherwise, false.
    """
    def validate_subscription(self) -> bool:
        current_date = datetime.now().timestamp()
        return self.active_subscription > current_date