from services.llm import call_llm

def critique(decision):
    return call_llm([
        {"role": "system", "content": "You are a strict insurance auditor."},
        {"role": "user", "content": f"""
Review this decision:

{decision}

Check:
- Policy violations
- Logical errors
- Missing reasoning

Give feedback.
"""}
    ])
