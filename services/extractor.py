from services.llm import call_llm
import json
import re

# -------- REGEX DATE HELPERS --------
def extract_date_regex(text):
    match = re.search(r"\b\d{1,2}-[A-Z]{3}-\d{4}\b", text)
    return match.group(0) if match else ""

# -------- REGEX NAME --------
def extract_name_regex(text):
    match = re.search(r"\b(MR|Mr|Mr\.)\.?\s+([A-Z][A-Z\s]+)", text)
    if match:
        return match.group(2).strip().title()
    return ""

# -------- MAIN EXTRACTION --------
def extract_fields(text, doc_type="claim"):

    prompt = f"""
Extract structured fields from this {doc_type}.

Return ONLY JSON:

{{
  "name": "",
  "policy_number": "",
  "vehicle": "",
  "incident_date": "",
  "policy_start_date": ""
}}

Rules:
- Extract real values only
- If missing → return ""
"""

    response = call_llm([
        {"role": "system", "content": "Extract structured insurance data."},
        {"role": "user", "content": prompt}
    ])

    try:
        data = json.loads(response)
    except:
        data = {}

    # 🔥 Fallbacks
    if doc_type == "policy":
        if not data.get("name"):
            data["name"] = extract_name_regex(text)

        if not data.get("policy_start_date"):
            data["policy_start_date"] = extract_date_regex(text)

    if doc_type == "claim":
        if not data.get("incident_date"):
            data["incident_date"] = extract_date_regex(text)

    return data
