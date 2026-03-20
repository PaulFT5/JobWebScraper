import os
from dotenv import load_dotenv
from groq import Groq
load_dotenv()
import os
from dotenv import load_dotenv
from groq import Groq
load_dotenv()


def LLM_activation(prompt, input):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{prompt}\n\nCV Text:\n{input}",
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content


