from pydantic import BaseModel

class UserInput(BaseModel):
    city: str
    days: str
    type: str
    month: str
    message_id: str = None
    role: str = None