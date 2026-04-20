from services.llm import call_llm
import json
import re

# -------- REGEX FALLBACK (STRICT) --------
def extract_name_regex(text):
    match = re.search(r"\b(MR|Mr|Mr\.)\.?\s+([A-Z][A-Z\s]+)", text)
    if match:
        return match.group(2).strip().title()
    return ""


# -------- MAIN EXTRACTION --------
def extract_fields(text, doc_type="claim"):

    prompt = f"""
Extract structured fields from this {doc_type} document.

STRICT RULES:
- Name must be a PERSON NAME (not headings)
- Ignore words like Motor, Policy, Liability
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

    # 🔥 fallback if LLM misses policy name
    if doc_type == "policy" and not data.get("name"):
        fallback = extract_name_regex(text)
        if fallback:
            data["name"] = fallback

    return data
