from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.vectorstore.qdrant import search_chunks

router = APIRouter(
    prefix="/retrieve",
    tags=["Document Retrieval"]
)

class RetrievalRequest(BaseModel):
    query: str
    document_id: int | None = None
    limit: int = Field(default=3,ge=1,le=10)

@router.post("/")
def retrieve_documents(request: RetrievalRequest):

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    try:
        results = search_chunks(
            query=request.query,
            document_id=request.document_id,
            limit=request.limit
        )

        return {
            "query": request.query,
            "results_count": len(results),
            "results": results
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Document retrieval failed"
        )