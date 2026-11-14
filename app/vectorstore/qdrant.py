
from uuid import uuid4

from qdrant_client import QdrantClient, models
from fastembed import TextEmbedding


client = QdrantClient(path="./qdrant_storage")

COLLECTION_NAME = "document_chunks"

embedding_model = TextEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def create_collection():
    collections = client.get_collections().collections
    existing_names = [collection.name for collection in collections]

    if COLLECTION_NAME not in [c.name for c in collections]:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=384,
                distance=models.Distance.COSINE
            )
        )
        return "Qdrant collection created successfully"

    return "Qdrant collection already exists"


def store_chunks(chunks, filename, chunking_strategy, document_id):

    embeddings = list(embedding_model.embed(chunks))

    points = []

    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

        points.append(
            models.PointStruct(
                id=str(uuid4()),
                vector=embedding.tolist(),
                payload={
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": index,
                    "text": chunk,
                    "chunking_strategy": chunking_strategy
                }
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return len(points)


def search_chunks(query,document_id= None,limit = 3):
    query_embedding = list(
        embedding_model.query_embed([query])
    )[0]
    search_filter = None
    if document_id is not None:
        search_filter = models.Filter(
            must = [
                models.FieldCondition(
                    key = "document_id",
                    match = models.MatchValue(value = document_id)
    
                )
            ]
        )

        results = client.query_points(
            collection_name= COLLECTION_NAME,
            query = query_embedding.tolist(),
            query_filter = search_filter,
            limit = limit,
            with_payload= True
        )

        return [{
            "score": point.score,
            "document_id": point.payload["document_id"],
            "filename": point.payload["filename"],
            "chunk_index": point.payload["chunk_index"],
            "text": point.payload["text"]
        }
            for point in results.points
        ]