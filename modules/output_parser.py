import json


ALLOWED_INSIGHT_TYPES = {
    "KPI Performance",
    "Anomaly / Risk",
    "Data Quality / Limitation",
}
REQUIRED_INSIGHT_FIELDS = {
    "insight_id",
    "type",
    "title",
    "narrative",
}
MARKDOWN_FENCE = chr(96) * 3


def _remove_markdown_fences(raw_text: str) -> str:
    """Remove an optional Markdown JSON fence without altering its content."""
    cleaned_text = raw_text.strip()

    if cleaned_text.startswith(f"{MARKDOWN_FENCE}json"):
        cleaned_text = cleaned_text[7:]
    elif cleaned_text.startswith(MARKDOWN_FENCE):
        cleaned_text = cleaned_text[3:]

    if cleaned_text.endswith(MARKDOWN_FENCE):
        cleaned_text = cleaned_text[:-3]

    return cleaned_text.strip()


def parse_response(raw_llm_text: str) -> list[dict]:
    """Return exactly three validated insights or raise ValueError."""
    if not isinstance(raw_llm_text, str) or not raw_llm_text.strip():
        raise ValueError("The AI response was empty.")

    cleaned_text = _remove_markdown_fences(raw_llm_text)

    try:
        parsed_data = json.loads(cleaned_text)
    except json.JSONDecodeError as error:
        raise ValueError("The AI response was not valid JSON.") from error

    if not isinstance(parsed_data, dict):
        raise ValueError("The AI response must be a JSON object.")
    if set(parsed_data) != {"insights"}:
        raise ValueError(
            "The AI response must contain only the 'insights' field."
        )

    insights = parsed_data["insights"]

    if not isinstance(insights, list) or len(insights) != 3:
        raise ValueError("The AI response must contain exactly three insights.")

    validated_insights = []

    for expected_id, insight in enumerate(insights, start=1):
        if not isinstance(insight, dict):
            raise ValueError(f"Insight {expected_id} must be a JSON object.")
        if set(insight) != REQUIRED_INSIGHT_FIELDS:
            raise ValueError(
                f"Insight {expected_id} has missing or unexpected fields."
            )

        insight_id = insight["insight_id"]
        insight_type = insight["type"]
        title = insight["title"]
        narrative = insight["narrative"]

        if type(insight_id) is not int or insight_id != expected_id:
            raise ValueError("Insight IDs must be exactly 1, 2, and 3 in order.")
        if insight_type not in ALLOWED_INSIGHT_TYPES:
            raise ValueError(
                f"Insight {expected_id} has an unsupported insight type."
            )
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"Insight {expected_id} has an empty title.")
        if not isinstance(narrative, str) or not narrative.strip():
            raise ValueError(f"Insight {expected_id} has an empty narrative.")

        validated_insights.append(
            {
                "insight_id": insight_id,
                "type": insight_type,
                "title": title.strip(),
                "narrative": narrative.strip(),
            }
        )

    return validated_insights