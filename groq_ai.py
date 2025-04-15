import os
from groq import Groq
from dotenv import load_dotenv
import re  

load_dotenv()
api_key = os.getenv("key")

client = Groq(api_key=api_key)

def get_ai_response(question):
    """Generates AI response from Groq model without <think> tags."""
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[{"role": "user", "content": question}],
        temperature=0.6,
        max_tokens=4096,
        top_p=0.95,
        stream=True,
    )

    response_text = ""

    for chunk in completion:
        response_text += chunk.choices[0].delta.content or ""

    clean_response = re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL).strip()

    return clean_response
