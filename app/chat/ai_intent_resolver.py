import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an intent classification system for an analytics platform.

You must respond ONLY with valid JSON.
Do not explain anything.

Rules:
- Use ONLY the provided allowed metrics
- Never invent metrics
- Never return SQL
- Never return explanations
"""

def ai_resolve_intent(
    user_query: str,
    context_name: str,
    allowed_metrics: list[str]
) -> dict:

    prompt = f"""
Context: {context_name}
Allowed metrics: {allowed_metrics}

User question:
"{user_query}"

Decide the intent.

Return one of the following JSON responses ONLY:

1) Run a metric:
{{
  "intent": "RUN_METRIC",
  "metric": "<metric_name>",
  "confidence": 0.0
}}

2) Ask for clarification:
{{
  "intent": "CLARIFY",
  "message": "<question>"
}}

3) Unsupported:
{{
  "intent": "UNSUPPORTED"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {"intent": "UNSUPPORTED"}
