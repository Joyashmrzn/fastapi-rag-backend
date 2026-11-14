
from app.llm.booking_agent import process_booking_message
from app.database.redis_memory import get_booking_state

conversation_id = "booking-test-002"

messages = [
    "I want to book an interview.",
    "My name is Ram Maharjan.",
    "My email is rammrzn1@example.com.",
    "I prefer November 21, 2026.",
    "11:30 AM."
]

for message in messages:

    print("\nUSER:", message)

    response = process_booking_message(
        conversation_id,
        message
    )

    print("ASSISTANT:", response)

    if response["booking_completed"]:
        break

print("\nFINAL REDIS STATE:")
print(get_booking_state(conversation_id))
