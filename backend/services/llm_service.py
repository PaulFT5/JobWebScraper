import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()


def llm_service(prompt, content):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{prompt}\n\nInput:\n{content}",
            }
        ],
        model="openai/gpt-oss-120b",
        max_tokens=2000
    )
    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content


