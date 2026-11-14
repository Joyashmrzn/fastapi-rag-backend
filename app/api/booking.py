
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr
from datetime import date, time

from app.database.booking_repo import save_interview_booking


router = APIRouter(
    prefix="/booking",
    tags=["Interview Booking"]
)


class BookingRequest(BaseModel):
    candidate_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    interview_date: date
    interview_time: time


@router.post("/")
def create_booking(request: BookingRequest):

    try:
        booking = save_interview_booking(
            candidate_name=request.candidate_name,
            email=str(request.email),
            interview_date=request.interview_date,
            interview_time=request.interview_time
        )

        return {
            "message": "Interview booked successfully",
            **booking
        }

    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=f"Booking failed: {str(ex)}"
        )
