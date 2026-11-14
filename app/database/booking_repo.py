
from sqlalchemy import text
from app.database.connection import engine


def save_interview_booking(
    candidate_name,
    email,
    interview_date,
    interview_time
):

    query = text("""
        INSERT INTO interview_bookings
        (candidate_name, email, interview_date, interview_time)
        VALUES (:candidate_name, :email, :interview_date, :interview_time)
        RETURNING id, candidate_name, email, interview_date, interview_time
    """)

    with engine.begin() as conn:
        result = conn.execute(
            query,
            {
                "candidate_name": candidate_name,
                "email": email,
                "interview_date": interview_date,
                "interview_time": interview_time
            }
        )

        booking = result.fetchone()

        return {
            "booking_id": booking.id,
            "candidate_name": booking.candidate_name,
            "email": booking.email,
            "interview_date": booking.interview_date,
            "interview_time": booking.interview_time
        }
