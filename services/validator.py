from services.extractor import extract_fields
import re
import unicodedata

# -------- NORMALIZE NAME --------
def normalize_name(name):
    if not name:
        return ""

    # Unicode normalize (fix hidden chars)
    name = unicodedata.normalize("NFKD", name)

    # Remove titles (Mr, Dr, etc.)
    name = re.sub(r"\b(mr|mrs|ms|dr)\.?\b", "", name, flags=re.IGNORECASE)

    # Remove special characters
    name = re.sub(r"[^a-zA-Z\s]", "", name)

    # Normalize spaces
    name = re.sub(r"\s+", " ", name)

    # Strip + lowercase
    return name.strip().lower()


# -------- VALIDATION --------
def validate_claim(claim_text, policy_text):

    claim_data = extract_fields(claim_text, "claim")
    policy_data = extract_fields(policy_text, "policy")

    claim_name = claim_data.get("name", "")
    policy_name = policy_data.get("name", "")

    claim_clean = normalize_name(claim_name)
    policy_clean = normalize_name(policy_name)

    # DEBUG (keep for now)
    print("CLAIM RAW:", repr(claim_name))
    print("POLICY RAW:", repr(policy_name))
    print("CLAIM CLEAN:", repr(claim_clean))
    print("POLICY CLEAN:", repr(policy_clean))

    issues = []

    # 🔴 NAME VALIDATION (robust)
    if claim_clean and policy_clean:
        if claim_clean not in policy_clean and policy_clean not in claim_clean:
            issues.append(f"Name mismatch: {claim_name} vs {policy_name}")
    else:
        issues.append("Could not extract name properly")

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
