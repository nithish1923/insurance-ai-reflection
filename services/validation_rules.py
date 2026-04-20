def check_mandatory_fields(claim_data, policy_data):

    missing = []

    # -------- CLAIM --------
    if not claim_data.get("name"):
        missing.append("Claim → Customer Name")

    if not claim_data.get("incident_date"):
        missing.append("Claim → Incident Date")

    # -------- POLICY --------
    if not policy_data.get("name"):
        missing.append("Policy → Policy Holder Name")

    if not policy_data.get("policy_start_date"):
        missing.append("Policy → Policy Start Date")

    return missing
