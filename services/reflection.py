from services.llm import call_llm

def improve(decision, feedback):
    return call_llm([
        {"role": "system", "content": "Improve decision using feedback."},
        {"role": "user", "content": f"""
Decision:
{decision}

Feedback:
{feedback}

Give FINAL improved decision.
"""}
    ])
