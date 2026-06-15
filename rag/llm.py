import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("api_key"))

def generate_llm_response(query, evidence_chunks):
    evidence_text = ""
    for i, chunk in enumerate(evidence_chunks, start=1):
        evidence_text += f"\nEvidence {i}:\n{chunk}\n"

    prompt = f"""You are Aegis, an AI-powered financial risk intelligence assistant.

Answer the user query using ONLY the retrieved evidence.

User Query:
{query}

Retrieved Evidence:
{evidence_text}

Provide:
1. Clear explanation
2. Risk insights
3. Professional reasoning"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"[DEBUG] Full error: {e}")
        return f"LLM Error: {e}"