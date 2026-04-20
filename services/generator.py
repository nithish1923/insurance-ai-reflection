from services.llm import call_llm

def generate_decision(claim, policy):
    return call_llm([
        {"role": "system", "content": "You are an expert insurance claim analyst."},
        {"role": "user", "content": f"""
Claim:
{claim}

Policy:
{policy}

Give:
- Decision
- Approved Amount
- Reason
"""}
    ])
