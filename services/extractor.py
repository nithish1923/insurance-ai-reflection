from services.llm import call_llm
import json
import re

# -------------------------
# NAME EXTRACTION (STRONG)
# -------------------------
def extract_name(text):
    # Pattern: Customer Name: XYZ
    match = re.search(r"customer name[:\-\s]*([A-Za-z\s]+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Pattern: MR. NAME
    match = re.search(r"\b(MR|Mr|Mr\.)\.?\s+([A-Z][A-Z\s]+)", text)
    if match:
        return match.group(2).strip().title()

    return ""


# -------------------------
# DATE EXTRACTION
# -------------------------
def extract_all_dates(text):
    return re.findall(r"\b\d{1,2}-[A-Z]{3}-\d{4}\b", text)


def extract_incident_date(text):
    match = re.search(
        r"incident date[:\-\s]*([\d]{1,2}-[A-Z]{3}-[\d]{4})",
        text,
        re.IGNORECASE
    )
    if match:
        return match.group(1)

    return ""


def extract_policy_start_date(text):
    match = re.search(
        r"(?:from|start date|policy start|issued on)[:\-\s]*([\d]{1,2}-[A-Z]{3}-[\d]{4})",
        text,
        re.IGNORECASE
    )
    if match:
        return match.group(1)

    # fallback → first date
    dates = extract_all_dates(text)
    return dates[0] if dates else ""


# -------------------------
# MAIN FUNCTION
# -------------------------
def extract_fields(text, doc_type="claim"):

    data = {
        "name": "",
        "policy_number": "",
        "vehicle": "",
        "incident_date": "",
        "policy_start_date": ""
    }

    # -------------------------
    # PRIORITY: REGEX EXTRACTION
    # -------------------------
    data["name"] = extract_name(text)

    if doc_type == "claim":
        data["incident_date"] = extract_incident_date(text)

    if doc_type == "policy":
        data["policy_start_date"] = extract_policy_start_date(text)

    # -------------------------
    # FALLBACK TO LLM ONLY IF MISSING
    # -------------------------
    if not data["name"] or (doc_type == "claim" and not data["incident_date"]):

        prompt = f"""
Extract structured fields from this {doc_type}.

Return JSON:

{{
  "name": "",
  "incident_date": "",
  "policy_start_date": ""
}}

Only extract if clearly present. No guessing.
"""

        response = call_llm([
            {"role": "system", "content": "Extract structured insurance data."},
            {"role": "user", "content": prompt + text}
        ])

        try:
            llm_data = json.loads(response)

            if not data["name"]:
                data["name"] = llm_data.get("name", "")

            if doc_type == "claim" and not data["incident_date"]:
                data["incident_date"] = llm_data.get("incident_date", "")

            if doc_type == "policy" and not data["policy_start_date"]:
                data["policy_start_date"] = llm_data.get("policy_start_date", "")

        except:
            pass

    return data
