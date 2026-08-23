import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "system",
            "content": """
You are a career learning-path expert.

The user will tell you their career goal and current skills.

Identify the important skills required for that career.
Do not assume the skills must exist in a particular course dataset.
Use your knowledge of the career domain.
"""
        },
        {
            "role": "user",
            "content": """
I want to become an App Developer in 6 months.
I currently know nothing.

Give me the important skills required
to become job-ready.

Return only a simple numbered list.
"""
        }
    ],
    temperature=0.2
)

print(response.choices[0].message.content)