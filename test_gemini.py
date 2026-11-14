
from app.llm.gemini import generate_response

answer = generate_response(
    "Explain what a REST API is in simple words."
)

print("Gemini Response:")
print(answer)
