
from fastapi import FastAPI
from sqlalchemy import text

from app.api.ingestion import router as ingestion_router
from app.api.chat import router as chat_router
from app.api.retrieval import router as retrieval_router

from app.vectorstore.qdrant import create_collection, store_chunks

from app.database.connection import engine, Base
from app.database import models

from app.api.booking import router as booking_router
# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Conversational RAG Backend",
    description="Backend for Document Ingestion and Conversational RAG",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "RAG Backend is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/db-test")
def database_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {
            "database": "Connected successfully",
            "result": result.scalar()
        }


@app.get("/qdrant-test")
def qdrant_test():
    result = create_collection()
    return {"qdrant": result}


@app.get("/embedding-test")
def embedding_test():
    sample_chunks = [
        "FastAPI is a Python framework for building APIs.",
        "PostgreSQL is a relational database management system."
    ]

    stored_count = store_chunks(
        chunks=sample_chunks,
        filename="test_document.txt",
        chunking_strategy="test"
    )

    return {
        "message": "Embeddings generated and stored successfully",
        "stored_vectors": stored_count
    }


app.include_router(ingestion_router)
app.include_router(chat_router)
app.include_router(retrieval_router)
app.include_router(booking_router)
