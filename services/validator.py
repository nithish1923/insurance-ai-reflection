from services.extractor import extract_fields

def validate_claim(claim_text, policy_text):

    claim_data = extract_fields(claim_text, "claim")
    policy_data = extract_fields(policy_text, "policy")

    issues = []

    # Name check
    if claim_data.get("name") and policy_data.get("name"):
        if claim_data["name"].lower() != policy_data["name"].lower():
            issues.append(f"Name mismatch: {claim_data['name']} vs {policy_data['name']}")

    # Policy number check
    if claim_data.get("policy_number") and policy_data.get("policy_number"):
        if claim_data["policy_number"] != policy_data["policy_number"]:
            issues.append(f"Policy number mismatch")

    # Vehicle check
    if claim_data.get("vehicle") and policy_data.get("vehicle"):
        if claim_data["vehicle"].lower() not in policy_data["vehicle"].lower():
            issues.append("Vehicle mismatch")

    if issues:
        return {"valid": False, "issues": issues}

    return {"valid": True, "issues": []}
