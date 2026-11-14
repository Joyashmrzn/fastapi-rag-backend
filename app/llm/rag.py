
from app.llm.gemini import generate_response
from app.vectorstore.qdrant import search_chunks
from app.database.redis_memory import get_conversation_history


def generate_rag_response(
    question,
    document_id=None,
    limit=3,
    conversation_id=None
):

    # 1. Retrieve relevant chunks from Qdrant
    retrieved_chunks = search_chunks(
        query=question,
        document_id=document_id,
        limit=limit
    )

    # 2. Retrieve previous conversation history
    history = []

    if conversation_id:
        history = get_conversation_history(conversation_id)

    conversation_context = "\n".join(
        [
            f"{message['role']}: {message['content']}"
            for message in history
        ]
    )

    # 3. Handle cases where no relevant documents are found
    if not retrieved_chunks:
        return {
            "answer": "I could not find relevant information in the uploaded documents.",
            "sources": []
        }

    # 4. Combine retrieved chunks into context
    context = "\n\n".join(
        [
            f"Source: {chunk['filename']}\n"
            f"Content: {chunk['text']}"
            for chunk in retrieved_chunks
        ]
    )

    # 5. Create prompt for Gemini
    prompt = f"""
You are a helpful document-based AI assistant.

Use the conversation history to understand follow-up questions
and references to previous messages.

Answer the current question using ONLY the information
provided in the document context below.

If the answer is not available in the context,
clearly say that the uploaded documents do not contain
enough information.

Do not invent facts or information.

Previous Conversation:
{conversation_context}

Document Context:
{context}

Current User Question:
{question}

Answer:
"""

    # 6. Generate answer using Gemini
    answer = generate_response(prompt)

    return {
        "answer": answer,
        "sources": [
            {
                "filename": chunk["filename"],
                "chunk_index": chunk["chunk_index"],
                "score": chunk["score"]
            }
            for chunk in retrieved_chunks
        ]
    }
