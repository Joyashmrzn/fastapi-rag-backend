
from fastapi import APIRouter, UploadFile, HTTPException, File, Form, Depends
from pypdf import PdfReader
from io import BytesIO
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session

from app.vectorstore.qdrant import store_chunks
from app.database.connection import get_db
from app.database.models import Document


router = APIRouter(
    prefix="/ingest",
    tags=["Document ingestion"]
)


@router.get("/")
def ingestion_status():
    return {
        "message": "Document Ingestion API is working"
    }


# Strategy 1: Fixed-size chunking
def fixed_size_chunking(text, chunk_size, chunk_overlap):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap

    return chunks


# Strategy 2: Recursive chunking
def recursive_chunking(text, chunk_size, chunk_overlap):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    return splitter.split_text(text)


@router.post("/")
async def upload_document(
    file: UploadFile = File(...),
    chunking_strategy: str = Form("fixed_size"),
    chunk_size: int = Form(500),
    chunk_overlap: int = Form(50),
    db: Session = Depends(get_db)
):


    filename = file.filename or ""
    extension = filename.lower().rsplit(".", 1)[-1]

    if extension not in ["pdf", "txt"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File size cannot exceed 10 MB"
        )


    try:
        if extension == "pdf":
            reader = PdfReader(BytesIO(content))

            if reader.is_encrypted:
                raise HTTPException(
                    status_code=400,
                    detail="Encrypted PDFs are not supported"
                )

            text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

            page_count = len(reader.pages)

        else:
            text = content.decode("utf-8-sig")
            page_count = None

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to extract text from this file"
        )

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No readable text found in the document"
        )

  
    chunking_strategy = (
        chunking_strategy.strip().lower().replace(" ", "_")
    )

    if chunking_strategy not in ["fixed_size", "recursive"]:
        raise HTTPException(
            status_code=400,
            detail="Choose fixed_size or recursive"
        )

   
    if chunk_size < 100 or chunk_size > 2000:
        raise HTTPException(
            status_code=400,
            detail="Chunk size must be between 100 and 2000"
        )

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise HTTPException(
            status_code=400,
            detail="Chunk overlap must be smaller than chunk size"
        )

    # 5. Apply chunking strategy
    if chunking_strategy == "fixed_size":
        chunks = fixed_size_chunking(
            text, chunk_size, chunk_overlap
        )
    else:
        chunks = recursive_chunking(
            text, chunk_size, chunk_overlap
        )


    try:
        document = Document(
            filename=filename,
            file_type=extension,
            page_count=page_count,
            character_count=len(text),
            chunking_strategy=chunking_strategy,
            chunk_count=len(chunks)
        )

        db.add(document)
        db.flush()

        
        stored_vectors = store_chunks(
            chunks=chunks,
            filename=filename,
            chunking_strategy=chunking_strategy,
            document_id=document.id
        )

        
        db.commit()
        db.refresh(document)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save document metadata or vectors"
        )

    
    return {
        "message": "Document uploaded and processed successfully",
        "document_id": document.id,
        "filename": filename,
        "file_type": extension,
        "page_count": page_count,
        "character_count": len(text),
        "chunking_strategy": chunking_strategy,
        "chunk_count": len(chunks),
        "chunks": chunks,
        "stored_vectors": stored_vectors
    }
