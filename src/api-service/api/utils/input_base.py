from pydantic import BaseModel


class UserInput(BaseModel):
    """
    UserInput is a Pydantic model that represents the input data for a user.

    Attributes:
        city (str): The city associated with the user input.
        days (str): The days associated with the user input.
        type (str): The type of input.
        month (str): The month associated with the user input.
        message_id (str, optional): The ID of the message, if any. Defaults to None.
        role (str, optional): The role associated with the user input, if any. Defaults to None.
    """

    city: str
    days: str
    type: str
    month: str
    message_id: str = None
    role: str = None
