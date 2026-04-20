from datetime import datetime

def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%d-%b-%Y")
    except:
        return None


def check_policy_validity(claim_data, policy_data):

    incident = parse_date(claim_data.get("incident_date", ""))
    start = parse_date(policy_data.get("policy_start_date", ""))

    # 🚨 Missing data → don't assume
    if not incident or not start:
        return {
            "valid": None,
            "reason": "Cannot verify policy validity (missing date)"
        }

    if incident < start:
        return {
            "valid": False,
            "reason": "Incident occurred before policy start date"
        }

    return {
        "valid": True,
        "reason": "Policy valid for incident date"
    }
