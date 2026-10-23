"""
Cerebras LLM Adapter
====================
Uses the Cerebras API (OpenAI-compatible) to generate natural language
responses grounded in RAG-retrieved financial context.
"""

from openai import OpenAI
import config

_client = OpenAI(
    api_key  = config.CEREBRAS_API_KEY,
    base_url = 'https://api.cerebras.ai/v1',
)

SYSTEM_PROMPT = """You are a financial analyst assistant at BCG GenAI Consulting,
helping Global Finance Corp. (GFC) analyze financial data.

CRITICAL RULES:
- Use ONLY the exact numbers from the "EXACT DATA" section provided in the context.
- Never invent, estimate, or approximate financial figures.
- If a number is not in the provided context, say you don't have that data.
- Use markdown: **bold** for key numbers, bullet points for lists.
- Be concise and professional. Add brief insight after presenting the data."""


def generate(query: str, context: str) -> str:
    """
    Generate a natural language response using Cerebras LLM.
    context: RAG-retrieved financial passages relevant to the query.
    """
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {
            'role': 'user',
            'content': (
                f"Financial context from 10-K filings:\n{context}\n\n"
                f"User question: {query}"
            )
        },
    ]

    response = _client.chat.completions.create(
        model       = config.CEREBRAS_MODEL,
        messages    = messages,
        max_tokens  = 512,
        temperature = 0.2,   # low temp for factual financial answers
    )

    return response.choices[0].message.content.strip()
