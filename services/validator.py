from services.extractor import extract_fields

INVALID_WORDS = ["motor", "policy", "liability", "period", "coverage"]

def is_valid_name(name):
    if not name:
        return False

    name_lower = name.lower()

    # reject if contains invalid keywords
    if any(word in name_lower for word in INVALID_WORDS):
        return False

    # reject if too short
    if len(name.split()) < 2:
        return False

    return True


def validate_claim(claim_text, policy_text):

    claim_data = extract_fields(claim_text, "claim")
    policy_data = extract_fields(policy_text, "policy")

    claim_name = claim_data.get("name")
    policy_name = policy_data.get("name")

    issues = []

    # 🔴 NAME VALIDATION
    if not is_valid_name(policy_name):
        issues.append("Could not reliably extract policy holder name")

    elif not is_valid_name(claim_name):
        issues.append("Could not reliably extract claimant name")

    else:
        if claim_name.lower() != policy_name.lower():
            issues.append(f"Name mismatch: {claim_name} vs {policy_name}")

    # 🔴 POLICY NUMBER
    if claim_data.get("policy_number") and policy_data.get("policy_number"):
        if claim_data["policy_number"] != policy_data["policy_number"]:
            issues.append("Policy number mismatch")

    # 🔴 VEHICLE
    if claim_data.get("vehicle") and policy_data.get("vehicle"):
        if claim_data["vehicle"].lower() not in policy_data["vehicle"].lower():
            issues.append("Vehicle mismatch")

    if issues:
        return {"valid": False, "issues": issues}

    return {"valid": True, "issues": []}
