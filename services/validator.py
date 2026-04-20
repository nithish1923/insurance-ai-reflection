from services.extractor import extract_fields
import re

# -------- fallback regex extraction --------
def extract_name_fallback(text):
    # Try common patterns
    patterns = [
        r"insured name[:\-]?\s*(.*)",
        r"name of insured[:\-]?\s*(.*)",
        r"mr\.?\s+[A-Za-z\s]+"
    ]

    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def validate_claim(claim_text, policy_text):

    claim_data = extract_fields(claim_text, "claim")
    policy_data = extract_fields(policy_text, "policy")

    # -------- fallback if LLM fails --------
    claim_name = claim_data.get("name") or extract_name_fallback(claim_text)
    policy_name = policy_data.get("name") or extract_name_fallback(policy_text)

    claim_policy_no = claim_data.get("policy_number")
    policy_no = policy_data.get("policy_number")

    claim_vehicle = claim_data.get("vehicle")
    policy_vehicle = policy_data.get("vehicle")

    issues = []

    # 🔴 NAME VALIDATION (STRICT)
    if claim_name and policy_name:
        if claim_name.lower() not in policy_name.lower():
            issues.append(f"Name mismatch: {claim_name} vs {policy_name}")
    else:
        issues.append("Unable to verify name (missing in document)")

    # 🔴 POLICY NUMBER
    if claim_policy_no and policy_no:
        if claim_policy_no != policy_no:
            issues.append("Policy number mismatch")

    # 🔴 VEHICLE
    if claim_vehicle and policy_vehicle:
        if claim_vehicle.lower() not in policy_vehicle.lower():
            issues.append("Vehicle mismatch")

    if issues:
        return {"valid": False, "issues": issues}

    return {"valid": True, "issues": []}
