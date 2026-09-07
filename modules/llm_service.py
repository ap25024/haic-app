import os

import groq
from dotenv import load_dotenv


MODEL_NAME = "openai/gpt-oss-120b"

INSIGHTS_SCHEMA = {
    "type": "object",
    "properties": {
        "insights": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "insight_id": {"type": "integer"},
                    "type": {
                        "type": "string",
                        "enum": [
                            "KPI Performance",
                            "Anomaly / Risk",
                            "Data Quality / Limitation",
                        ],
                    },
                    "title": {"type": "string"},
                    "narrative": {"type": "string"},
                },
                "required": [
                    "insight_id",
                    "type",
                    "title",
                    "narrative",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["insights"],
    "additionalProperties": False,
}


def fetch_llm_response(prompt: str) -> str:
    """Send a prompt to Groq and return a JSON response as text."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("The LLM prompt cannot be empty.")

    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("No GROQ_API_KEY found. Please check your .env file.")

    client = groq.Groq(api_key=api_key, max_retries=0, timeout=60.0)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Senior Data Analyst. Return only the "
                        "requested structured JSON response."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "business_insights",
                    "strict": True,
                    "schema": INSIGHTS_SCHEMA,
                },
            },
            temperature=0.7,
            max_completion_tokens=2048,
            reasoning_effort="medium"
        )
    except groq.RateLimitError as error:
        raise RuntimeError(
            "The free Groq API limit has been reached. Please try again later."
        ) from error
    except groq.APIConnectionError as error:
        raise RuntimeError(
            "The Groq API could not be reached. Please check your connection."
        ) from error
    except groq.APIStatusError as error:
        if error.status_code >= 500:
            message = "The Groq service is temporarily unavailable."
        else:
            message = f"The Groq request failed (HTTP {error.status_code})."
        raise RuntimeError(message) from error

    content = response.choices[0].message.content
    if not content or not content.strip():
        raise RuntimeError("The LLM returned an empty response.")

    return content.strip()
