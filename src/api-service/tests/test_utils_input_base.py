from api.utils.input_base import UserInput


def test_valid_user_input():
    """Test creating a UserInput object with valid input."""
    input_data = {
        "city": "New York",
        "days": "7",
        "type": "forecast",
        "month": "November",
        "message_id": "12345",
        "role": "user",
    }
    user_input = UserInput(**input_data)

    # Verify the input is correctly parsed
    assert user_input.city == "New York"
    assert user_input.days == "7"
    assert user_input.type == "forecast"
    assert user_input.month == "November"
    assert user_input.message_id == "12345"
    assert user_input.role == "user"


def test_optional_fields():
    """Test that optional fields can be omitted."""
    input_data = {
        "city": "London",
        "days": "3",
        "type": "forecast",
        "month": "December",
    }
    user_input = UserInput(**input_data)

    # Verify required fields are set correctly
    assert user_input.city == "London"
    assert user_input.days == "3"
    assert user_input.type == "forecast"
    assert user_input.month == "December"

    # Optional fields should be None
    assert user_input.message_id is None
    assert user_input.role is None
