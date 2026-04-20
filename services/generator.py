from services.llm import call_llm
import json

def generate_decision(claim, policy):

    prompt = f"""
You are an expert insurance claim analyst.

STRICT RULES:
- Only use given policy
- Do NOT assume anything

Return ONLY JSON:

{{
  "decision": "Approve / Reject / Partial / Conditional",
  "approved_amount": number,
  "confidence": number (0-100),
  "reasons": ["reason1", "reason2"],
  "explainability": "step-by-step explanation"
}}

---

CLAIM:
{claim}

---

POLICY:
{policy}
"""

    response = call_llm([
        {"role": "system", "content": "You generate structured insurance decisions."},
        {"role": "user", "content": prompt}
    ])

    try:
        return json.loads(response)
    except:
        return {
            "decision": "Error",
            "approved_amount": 0,
            "confidence": 0,
            "reasons": ["Failed to parse output"],
            "explainability": response
        }
