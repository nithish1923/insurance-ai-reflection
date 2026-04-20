from services.llm import call_llm
import json
import re

# -------------------------
# EXTRACT ALL DATES
# -------------------------
def extract_all_dates(text):
    return re.findall(r"\b\d{1,2}-[A-Z]{3}-\d{4}\b", text)


# -------------------------
# INCIDENT DATE (CLAIM)
# -------------------------
def extract_incident_date(text):
    match = re.search(
        r"incident date[:\-\s]*([\d]{1,2}-[A-Z]{3}-[\d]{4})",
        text,
        re.IGNORECASE
    )
    if match:
        return match.group(1)

    # fallback → first date found
    dates = extract_all_dates(text)
    return dates[0] if dates else ""


# -------------------------
# POLICY START DATE
# -------------------------
def extract_policy_start_date(text):
    match = re.search(
        r"(?:from|start date|policy start)[:\-\s]*([\d]{1,2}-[A-Z]{3}-[\d]{4})",
        text,
        re.IGNORECASE
    )
    if match:
        return match.group(1)

    # fallback → first date in policy doc
    dates = extract_all_dates(text)
    return dates[0] if dates else ""


# -------------------------
# NAME (REGEX FALLBACK)
# -------------------------
def extract_name_regex(text):
    match = re.search(r"\b(MR|Mr|Mr\.)\.?\s+([A-Z][A-Z\s]+)", text)
    if match:
        return match.group(2).strip().title()
    return ""


# -------------------------
# MAIN EXTRACTION FUNCTION
# -------------------------
def extract_fields(text, doc_type="claim"):

    prompt = f"""
Extract structured fields from this {doc_type} document.

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
- Do not hallucinate
- If missing → return ""
"""

    response = call_llm([
        {"role": "system", "content": "Extract structured insurance data accurately."},
        {"role": "user", "content": prompt}
    ])

    try:
        data = json.loads(response)
    except:
        data = {}

    # -------------------------
    # FALLBACKS
    # -------------------------

    # Name fallback
    if not data.get("name"):
        data["name"] = extract_name_regex(text)

    # Claim → Incident date
    if doc_type == "claim":
        if not data.get("incident_date"):
            data["incident_date"] = extract_incident_date(text)

    # Policy → Start date
    if doc_type == "policy":
        if not data.get("policy_start_date"):
            data["policy_start_date"] = extract_policy_start_date(text)

    return data
