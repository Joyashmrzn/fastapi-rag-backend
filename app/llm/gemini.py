
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.5-flash-lite"


def generate_response(prompt):
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            return response.text

        except errors.ServerError as e:
            if attempt == 2:
                raise

            print(f"Gemini temporarily unavailable. Retrying...")
            time.sleep(2 ** (attempt + 1))
