import re

# -------- Extract field using regex --------
def extract_field(text, field_name):
    pattern = rf"{field_name}[:\-]\s*(.*)"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


# -------- Main validation function --------
def validate_claim(claim_text, policy_text):

    claim_name = extract_field(claim_text, "Customer Name")
    policy_name = extract_field(policy_text, "Insured Name")

    claim_policy_no = extract_field(claim_text, "Policy Number")
    policy_no = extract_field(policy_text, "Policy No")

    errors = []

    # 🔴 Name mismatch
    if claim_name and policy_name:
        if claim_name.lower() != policy_name.lower():
            errors.append(f"Name mismatch: Claim by '{claim_name}', Policy holder is '{policy_name}'")

    # 🔴 Policy number mismatch
    if claim_policy_no and policy_no:
        if claim_policy_no != policy_no:
            errors.append(f"Policy number mismatch: Claim has '{claim_policy_no}', Policy is '{policy_no}'")

    if errors:
        return False, errors

    return True, ["Validation passed"]
