# FastAPI RAG Backend

this project is built with FastAPI mainly covering the backend tasks that implemetns document ingestion,RAG, conversational memeory and AI powered interview booking system 

This project allows users to :
    1.) upload pdf or txt files 
    2.) processing and storing content as vector emeddings 
    3.) retieve information through semantic search and interact with an AI assistant using conversational API

# its features are :
1. **Document Ingestion**

    -Upload PDF and TXT documents.

    -Extract text from uploaded documents.

    -Supports two chunking strategies:

    -Fixed-size chunking

    -Recursive character chunking

    -Generate embeddings using FastEmbed.

    -Store vectors in Qdrant.

    -Save document metadata in PostgreSQL.

2. **Document Retrieval**

    -Perform semantic search on stored document chunks.

    -Retrieve relevant content based on user queries.

    -Optionally filter results by document ID.

3. **Conversational RAG**

    -Generate context-aware answers using retrieved document content.

    -Use Gemini as the language model.

    -Maintain multi-turn conversations.

    -Store conversation history using Redis.

    -Return source information with generated answers.

4. **AI-Powered Interview Booking**

    -Collect candidate name, email, interview date, and time through conversation.

    -Extract booking details using Gemini.

    -Maintain incomplete booking information using Redis.

    -Validate booking details.

    -Store confirmed interview bookings in PostgreSQL.

5. **REST API**

    -Built using FastAPI.

    -Interactive API documentation through Swagger UI.

    -Modular API structure.

# Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | REST API development |
| PostgreSQL | Document metadata and interview booking storage |
| SQLAlchemy | Database interaction |
| Qdrant | Vector database for storing and retrieving embeddings |
| FastEmbed | Text embedding generation |
| LangChain Text Splitters | Recursive text chunking |
| Redis | Conversational memory and temporary booking state |
| Google Gemini | LLM for RAG responses and interview booking |
| PyPDF | PDF text extraction |
| Pydantic | Request validation and data modelling |

# API Documentation

FastAPI provides interactive API documentation through Swagger UI.
Open the following URL in your browser: http://127.0.0.1:8000/docs

You can use Swagger UI to test the available API endpoints.

# API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ingest/` | Upload and process PDF or TXT documents |
| POST | `/retrieve/` | Retrieve relevant document chunks using semantic search |
| POST | `/chat/` | Ask questions and interact with the conversational RAG assistant |
| POST | `/booking/` | Create an interview booking |

# Running Tests

The project includes individual test scripts for testing different components.

Run the following commands from the project root:

    python test_gemini.py
    python test_rag.py
    python test_redis.py
    python test_redis_memory.py
    python test_booking_agent.py