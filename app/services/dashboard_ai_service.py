from openai import OpenAI
import os
import json
from app.utils.json_safe import make_json_safe


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)


class DashboardAIService:

    @staticmethod
    def generate_insights(context_name: str, dashboard: dict):

        safe_dashboard = make_json_safe(dashboard)

        prompt = f"""
You are an ERP business analyst.

Context: {context_name}

Dashboard Data:
{json.dumps(safe_dashboard, indent=2, default=str)}

Rules:
- Do not invent numbers
- Do not restate raw data
- Provide insights, risks, and recommendations

Return JSON with keys:
summary, insights, risks, recommendations
"""

        client = get_openai_client()

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an ERP business analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        # ✅ THIS IS THE FIX
        return json.loads(response.choices[0].message.content)
