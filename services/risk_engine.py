def calculate_risk(validation_result, claim_text):

    score = 0
    reasons = []

    # Validation issues
    if not validation_result.get("valid"):
        score += 50
        reasons.append("Validation failure")

    # High amount
    if "50000" in claim_text or "₹50,000" in claim_text:
        score += 10
        reasons.append("High claim amount")

    # Missing FIR (example)
    if "theft" in claim_text.lower() and "fir" not in claim_text.lower():
        score += 30
        reasons.append("Missing FIR")

    # Risk level
    if score < 30:
        level = "Low"
    elif score < 60:
        level = "Medium"
    else:
        level = "High"

    return {
        "score": score,
        "level": level,
        "reasons": reasons
    }
