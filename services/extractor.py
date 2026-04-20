from services.llm import call_llm
import json

def extract_fields(text, doc_type="claim"):

    prompt = f"""
Extract structured fields from this {doc_type} document.

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
        {"role": "system", "content": "You extract structured data from documents."},
        {"role": "user", "content": prompt}
    ])

    try:
        return json.loads(response)
    except:
        return {}
