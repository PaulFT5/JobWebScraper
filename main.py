from google import genai
import os
from dotenv import load_dotenv
#use groq
load_dotenv()

key = os.getenv("GEMINI_API_KEY")
print("Key:", key[:8] if key else "NOT FOUND")

client = genai.Client(api_key=key)

response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents="Say hello in one word"
)

print(response.text)