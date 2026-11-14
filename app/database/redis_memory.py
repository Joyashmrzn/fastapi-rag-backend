import json
from app.database.redis_client import redis_client

CHAT_TTL = 86400
MAX_HISTORY = 20


def save_message(conversation_id, role, content):
    key = f"chat:{conversation_id}"

    message = {
        "role": role,
        "content": content
    }

    redis_client.rpush(key, json.dumps(message))

    redis_client.ltrim(key, -MAX_HISTORY, -1)
    redis_client.expire(key, CHAT_TTL)


def get_conversation_history(conversation_id):
    key = f"chat:{conversation_id}"

    messages = redis_client.lrange(key, 0, -1)

    return [
        json.loads(message)
        for message in messages
    ]


def clear_conversation(conversation_id):
    key = f"chat:{conversation_id}"
    redis_client.delete(key)

def save_booking_state(conversation_id,booking_data):
    key = f"booking:{conversation_id}"

    redis_client.setex(
        key,
        CHAT_TTL,
        json.dumps(booking_data)
    )

def get_booking_state(conversation_id):
    key = f"booking:{conversation_id}"

    data = redis_client.get(key)

    if data:
        return json.loads(data)
    return None

def clear_booking_state(conversation_id):
    key = f"booking:{conversation_id}"
    redis_client.delete(key)