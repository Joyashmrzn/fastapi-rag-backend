from app.database.redis_client import redis_client
from app.database.redis_memory import (
    save_message,
    get_conversation_history,
    clear_conversation
)

conversation_id = "test-conversation-001"
key = f"chat:{conversation_id}"

# Clear previous test data
clear_conversation(conversation_id)

# Save messages
save_message(conversation_id, "user", "What is AMS?")
save_message(
    conversation_id,
    "assistant",
    "AMS stands for Admission Management System."
)

# Check Redis directly
print("\nDIRECT REDIS CHECK:")
print("Keys:", redis_client.keys("*"))
print("Raw messages:", redis_client.lrange(key, 0, -1))

# Check our retrieval function
print("\nFUNCTION RETRIEVAL:")
history = get_conversation_history(conversation_id)
print(history)

# Clear test data
clear_conversation(conversation_id)