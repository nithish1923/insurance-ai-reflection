from services.llm import call_llm

def generate_decision(claim, policy):

    return call_llm([
        {
            "role": "system",
            "content": """
You are an expert insurance claim analyst.

STRICT RULES:
- Only use the provided policy text
- Do NOT assume any rules
- If something is not mentioned → say "Not specified in policy"
- Be realistic and professional
"""
        },
        {
            "role": "user",
            "content": f"""
Claim:
{claim}

Policy:
{policy}

Task:
Analyze the claim strictly based on policy.

Output format:
- Decision (Approve / Reject / Partial / Conditional)
- Approved Amount
- Reason (clear, policy-based)
"""
        }
    ])
