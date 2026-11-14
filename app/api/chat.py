from fastapi import APIRouter,HTTPException
from pydantic import BaseModel, Field 
from app.llm.rag import generate_rag_response
from uuid import uuid4
from app.database.redis_memory import save_message
from app.llm.booking_agent import process_booking_message
from app.database.redis_memory import get_booking_state

router = APIRouter(
    prefix = "/chat",
    tags=["Conversational RAG"]
)
class ChatRequest(BaseModel):
    question: str
    document_id: int | None = None
    limit: int = Field(default=3,ge=1,le=10)
    conversation_id: str| None=None

def is_booking_request(question):
        keywords = [
            "book an interview",
            "schedule an interview",
            "interview booking",
            "book interview",
            "schedule interview",
            "want to book",
            "interview appointment"
        ]

        question = question.lower()
        return any(keyword in question for keyword in keywords)


@router.get("/")
def chat_status():
    return{
    " message": "Chat API is working"
}


@router.post("/")
def chat(request: ChatRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    conversation_id = request.conversation_id or str(uuid4())

    try:
        
        save_message( # Save user message in Redis
            conversation_id,
            "user",
            request.question
        )

        
        booking_state = get_booking_state(conversation_id)# Check for ongoing booking

        if booking_state is not None or is_booking_request(request.question):

            result = process_booking_message(
                conversation_id,
                request.question
            )

            answer = result["message"]

            save_message(
                conversation_id,
                "assistant",
                answer
            )

            # Return booking response
            return {
                "conversation_id": conversation_id,
                "question": request.question,
                "answer": answer,
                "booking_completed": result["booking_completed"],
                "booking_details": {
                    key: value
                    for key, value in result.items()
                    if key not in ["message", "booking_completed"]
                }
            }

        # Normal RAG conversation
        result = generate_rag_response(
            question=request.question,
            document_id=request.document_id,
            limit=request.limit,
            conversation_id=conversation_id
        )

        save_message(
            conversation_id,
            "assistant",
            result["answer"]
        )

        return {
            "conversation_id": conversation_id,
            "question": request.question,
            "document_id": request.document_id,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(ex)}"
        )
