from services.llm import call_llm
import json
import re

def extract_name_regex(text):
    """
    Strict regex for names like:
    MR. KONDAPAKA NITHISH
    """
    match = re.search(r"\b(MR|Mr|Mr\.)\.?\s+([A-Z][A-Z\s]+)", text)
    if match:
        name = match.group(2).strip()
        return name.title()  # convert to proper case
    return ""


def extract_fields(text, doc_type="claim"):

    prompt = f"""
Extract structured fields from this {doc_type} document.

STRICT RULES:
- Name must be a PERSON NAME
- Ignore headings like Motor, Policy, Liability
- If unsure → return empty string

Return ONLY JSON:

{{
  "name": "",
  "policy_number": "",
  "vehicle": ""
}}

Document:
{text}
"""

    response = call_llm([
        {"role": "system", "content": "You extract accurate structured data."},
        {"role": "user", "content": prompt}
    ])

    try:
        data = json.loads(response)
    except:
        data = {}

    # 🔥 FALLBACK for policy name
    if doc_type == "policy" and not data.get("name"):
        fallback_name = extract_name_regex(text)
        if fallback_name:
            data["name"] = fallback_name

    return data
