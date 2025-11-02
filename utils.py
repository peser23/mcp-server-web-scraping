import trafilatura
import os
from groq import Groq

def clean_html_to_text(html):
    try:
        extracted = trafilatura.extract(
            html,
            include_comments = False,
            include_tables=False,
            favor_recall=False
        )
        if extracted:
            return extracted
    except Exception as ex:
        raise ex
    
def get_response_from_llm(user_prompt, system_prompt):
    api_key = os.getenv("GROQ_API_KEY")
    groq_client = Groq(api_key=api_key)

    completion = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system", "content": system_prompt
            },
            {
                "role": "user", "content": user_prompt
            }
        ]
    )
    return completion.choices[0].message.content
