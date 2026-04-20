from services.llm import call_llm

def debate(claim, policy):

    approve = call_llm([
        {"role": "system", "content": "You support approving claims."},
        {"role": "user", "content": f"{claim}\nPolicy:\n{policy}"}
    ])

    reject = call_llm([
        {"role": "system", "content": "You reject risky claims."},
        {"role": "user", "content": f"{claim}\nPolicy:\n{policy}"}
    ])

    final = call_llm([
        {"role": "system", "content": "You are a judge."},
        {"role": "user", "content": f"""
Approve:
{approve}

Reject:
{reject}

Give best final decision.
"""}
    ])

    return approve, reject, final
