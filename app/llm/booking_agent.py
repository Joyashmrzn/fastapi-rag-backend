
import json
from datetime import date, time, datetime

from app.llm.gemini import generate_response
from app.database.redis_memory import (
    save_booking_state,
    get_booking_state,
    clear_booking_state
)
from app.database.booking_repo import save_interview_booking
from pydantic import BaseModel, EmailStr, ValidationError, Field

class BookingDetails(BaseModel):
    candidate_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    interview_date: date
    interview_time: time


def parse_json_response(response):
    response = response.strip()

    if response.startswith("```"):
        response = response.split("\n", 1)[1]
        response = response.rsplit("```", 1)[0]

    return json.loads(response)


def extract_booking_details(message, current_state):

    prompt = f"""
You are an interview booking assistant.

Extract interview booking details from the user's message.

Required fields:
- candidate_name
- email
- interview_date (YYYY-MM-DD)
- interview_time (HH:MM in 24-hour format)

Existing booking details:
{json.dumps(current_state)}

User message:
{message}

Rules:
1. Keep previously collected details unless the user corrects them.
2. Extract only information explicitly provided by the user.
3. Convert understandable dates and times into the required formats.
4. Use null for missing information.
5. Do not invent any information.
6. Return ONLY valid JSON in this exact structure:

{{
    "candidate_name": null,
    "email": null,
    "interview_date": null,
    "interview_time": null
}}
"""

    response = generate_response(prompt)

    try:
        return parse_json_response(response)
    except json.JSONDecodeError:
        raise ValueError("Could not understand booking details.")

def process_booking_message(conversation_id, message):

    current_state = get_booking_state(conversation_id) or {}

    extracted = extract_booking_details(
        message,
        current_state
    )

    booking_data = {
        **current_state,
        **{
            key: value
            for key, value in extracted.items()
            if value is not None
        }
    }

    required_fields = [
        "candidate_name",
        "email",
        "interview_date",
        "interview_time"
    ]

    missing_fields = [
        field for field in required_fields
        if not booking_data.get(field)
    ]

    if missing_fields:
        save_booking_state(conversation_id, booking_data)

        questions = {
            "candidate_name": "May I have your full name?",
            "email": "What is your email address?",
            "interview_date": "Which date would you prefer for the interview?",
            "interview_time": "What time would you prefer?"
        }

        return {
            "booking_completed": False,
            "message": questions[missing_fields[0]]
        }


    try:
        validated = BookingDetails(**booking_data)

        if validated.interview_date < date.today():
            return {
                "booking_completed": False,
                "message": "That date is in the past. Please provide a future interview date."
            }

        booking = save_interview_booking(
            candidate_name=validated.candidate_name,
            email=str(validated.email),
            interview_date=validated.interview_date,
            interview_time=validated.interview_time
        )

        clear_booking_state(conversation_id)

        return {
            "booking_completed": True,
            "message": "Your interview has been booked successfully!",
            **booking
        }

    except ValidationError:
        return {
            "booking_completed": False,
            "message": "Some booking details are invalid. Please provide valid name, email, date, and time."
        }

