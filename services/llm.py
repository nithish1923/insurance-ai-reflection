from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not set")

client = OpenAI(api_key=api_key)

def call_llm(messages, temperature=0.3):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content
