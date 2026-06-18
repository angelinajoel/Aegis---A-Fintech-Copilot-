import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("api_key")
)


def generate_llm_response(query, evidence_chunks):

    evidence_text = "\n\n".join(evidence_chunks)

    prompt = f"""
You are Aegis, an elite Financial Risk Intelligence AI.

Your job is to provide natural, professional, human-like responses.

Rules:
- Use ONLY the provided evidence.
- Do NOT mention chunks or evidence numbers.
- Do NOT say "Based on the retrieved evidence".
- Answer naturally like ChatGPT.
- Be concise but informative.
- If relevant, explain financial, compliance, AML, KYC, fraud, or risk concepts clearly.
- If the evidence does not contain enough information, say so honestly.

Question:
{query}

Knowledge Base:
{evidence_text}
"""

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": """
You are Aegis AI.

You are a professional financial risk analyst,
fraud investigator,
AML specialist,
and compliance expert.

Respond naturally and professionally.

Do not use numbered sections unless absolutely necessary.
Write like an intelligent human advisor.
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.3,
            max_tokens=1000
        )

        return response.choices[0].message.content

    except Exception as e:

        print(f"[DEBUG] Full error: {e}")

        return f"LLM Error: {e}"