import pytest
import os
import json
from datetime import datetime
from api.utils.chat_utils import ChatHistoryManager

@pytest.fixture
def chat_manager(tmp_path):
    """Fixture to initialize ChatHistoryManager with a temporary directory."""
    model_name = "test-model"
    history_dir = tmp_path / "chat-history"
    return ChatHistoryManager(model=model_name, history_dir=str(history_dir))

@pytest.fixture
def sample_chat_data():
    """Fixture to provide sample chat data."""
    return {
        "chat_id": "12345",
        "dts": datetime.now().timestamp(),
        "messages": [
            {"sender": "user", "text": "Hello"},
            {"sender": "bot", "text": "Hi there!"},
        ],
    }

@pytest.fixture
def session_id():
    """Fixture to provide a sample session ID."""
    return "session-1"

def test_save_chat(chat_manager, sample_chat_data, session_id):
    """Test saving a chat."""
    chat_manager.save_chat(sample_chat_data, session_id)

    # Verify the file was created
    expected_filepath = chat_manager._get_chat_filepath(sample_chat_data["chat_id"], session_id)
    assert os.path.exists(expected_filepath)

    # Verify the contents of the saved file
    with open(expected_filepath, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
        assert saved_data == sample_chat_data

def test_get_chat(chat_manager, sample_chat_data, session_id):
    """Test retrieving a saved chat."""
    chat_manager.save_chat(sample_chat_data, session_id)

    retrieved_chat = chat_manager.get_chat(sample_chat_data["chat_id"], session_id)
    assert retrieved_chat == sample_chat_data

def test_get_recent_chats(chat_manager, sample_chat_data, session_id):
    """Test retrieving recent chats."""
    # Save multiple chats
    for i in range(5):
        chat_data = {**sample_chat_data, "chat_id": f"chat-{i}", "dts": sample_chat_data["dts"] + i}
        chat_manager.save_chat(chat_data, session_id)

    # Retrieve recent chats
    recent_chats = chat_manager.get_recent_chats(session_id, limit=3)
    assert len(recent_chats) == 3

    # Verify order (most recent first)
    assert recent_chats[0]["chat_id"] == "chat-4"
    assert recent_chats[1]["chat_id"] == "chat-3"
    assert recent_chats[2]["chat_id"] == "chat-2"

def test_get_chat_nonexistent(chat_manager, session_id):
    """Test attempting to retrieve a non-existent chat."""
    retrieved_chat = chat_manager.get_chat("nonexistent-chat", session_id)
    assert retrieved_chat == {}

def test_save_chat_error_handling(chat_manager, session_id, mocker):
    """Test error handling during save_chat."""
    sample_chat = {"chat_id": "12345"}
    
    # Mock json.dump to raise an exception
    mocker.patch("json.dump", side_effect=Exception("Mocked exception"))
    
    with pytest.raises(Exception, match="Mocked exception"):
        chat_manager.save_chat(sample_chat, session_id)

def test_get_chat_error_handling(chat_manager, session_id, mocker):
    """Test error handling during get_chat."""
    filepath = chat_manager._get_chat_filepath("12345", session_id)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write("invalid-json")
    
    chat_data = chat_manager.get_chat("12345", session_id)
    assert chat_data == {}