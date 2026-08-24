import json


def assemble_prompt(domain, audience, goal, eda_package):
    """
    Constructs a context-aware prompt using the user's business
    context and the structured EDA results.
    """

    eda_context = json.dumps(
        eda_package,
        indent=2,
        default=str
    )


    prompt = f"""
You are a Senior Data Analyst and Business Intelligence Consultant.

Your task is to interpret structured Exploratory Data Analysis (EDA)
results and communicate the most useful findings for a business audience.


BUSINESS CONTEXT

Domain:
{domain}

Target Audience:
{audience}

Primary Analysis Goal:
{goal}


STRUCTURED EDA RESULTS

{eda_context}


TASK

Generate exactly THREE Business Intelligence insights based on the available EDA results and the business context.
Each insight must belong to ONE of the following categories:

1. KPI Performance

Use when the descriptive statistics or other available EDA results provide a meaningful observation about an important business metric.

2. Anomaly / Risk

Use when the EDA identifies unusual numerical observations, outliers, potentially concerning patterns, or information that may
deserve further investigation.


3. Data Quality / Limitation

Use when missing values, limited observations, data quality issues, or other limitations may affect the reliability or usefulness of
the analysis.

The three insights do NOT need to use three different categories.

For example, two insights may both be KPI Performance if these are the most relevant findings in the dataset.

INSIGHT SELECTION RULES

- Generate exactly THREE insights.
- Select only findings that are supported by the supplied EDA.
- Prioritize findings that relate to the user's Primary Analysis Goal.
- Consider the Domain when deciding what is business-relevant.
- Tailor the explanation to the Target Audience.
- Prefer meaningful business findings over trivial statistical observations.
- Do not force a particular insight category when the data does not support it.
- Multiple insights may belong to the same category.
- Correlations may be used as supporting evidence when relevant,
  but correlation alone does not establish causation.


ACCURACY RULES

- Every numerical statement must come directly from the supplied EDA.
- Never invent numbers.
- Never invent categories or observations.
- Never invent trends or changes over time.
- Never claim that one variable causes another based only on correlation.
- Do not make unsupported predictions.
- Do not make unsupported business recommendations.
- Do not describe an outlier as an error, fraud, or failure unless the
  supplied data explicitly supports that conclusion.
- Clearly distinguish an observed result from a possible business implication.
- If the available evidence is weak, communicate that limitation rather
  than inventing a stronger conclusion.


WRITING STYLE

- Use concise, readable, professional Business Intelligence language.
- Write for the specified Target Audience.
- Avoid unnecessary statistical terminology.
- Explain why each finding may matter.
- Avoid generic observations that could apply to any dataset.
- Each narrative should be short and focused.

OUTPUT FORMAT

Return ONLY valid JSON.

Do not return Markdown.
Do not use code fences.
Do not provide an introduction.
Do not provide a conclusion.
Do not provide any text outside the JSON object.

Return exactly this structure:

{{
    "insights": [
        {{
            "insight_id": 1,
            "type": "KPI Performance",
            "title": "Short descriptive title",
            "narrative": "Concise explanation of the finding and why it may matter."
        }},
        {{
            "insight_id": 2,
            "type": "Anomaly / Risk",
            "title": "Short descriptive title",
            "narrative": "Concise explanation of the finding and why it may matter."
        }},
        {{
            "insight_id": 3,
            "type": "Data Quality / Limitation",
            "title": "Short descriptive title",
            "narrative": "Concise explanation of the finding and why it may matter."
        }}
    ]
}}

The type values shown above are examples of the required structure.

For each insight, choose the most appropriate type from:

- KPI Performance
- Anomaly / Risk
- Data Quality / Limitation

Do not assume that all three types must appear.
"""

    return prompt