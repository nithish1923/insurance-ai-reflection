from services.llm import call_llm
import json

def extract_fields(text, doc_type="claim"):

    prompt = f"""
Extract structured fields from this {doc_type} document.

STRICT RULES:
- Extract ONLY real values
- Name must be a PERSON NAME (not headings)
- Ignore words like: Motor, Policy, Liability, Period, Coverage
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
        {"role": "system", "content": "You extract accurate structured data from insurance documents."},
        {"role": "user", "content": prompt}
    ])

    try:
        return json.loads(response)
    except:
        return {}
