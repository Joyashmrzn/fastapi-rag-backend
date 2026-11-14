
from app.llm.rag import generate_rag_response

result = generate_rag_response(
    question="What is the Admission Management System?",
    document_id=1
)

print("\nRAG RESPONSE:")
print(result["answer"])

print("\nRETRIEVED SOURCES:")
for source in result["sources"]:
    print(source)
