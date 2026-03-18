import os
from dotenv import load_dotenv
from groq import Groq
load_dotenv()
import os
from dotenv import load_dotenv
from groq import Groq
load_dotenv()


def LLM_activation(text):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Return skills as a JSON object with two keys: 'technical' and 'soft', each containing a list of skills.\n\nCV Text:\n{text}",
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    print(chat_completion.choices[0].message.content)

