from services.llm import call_llm
import json
import re

def extract_json(text):
    """
    Extract JSON from messy LLM response
    """
    try:
        # direct parse
        return json.loads(text)
    except:
        pass

    # try extracting JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass

    return None


def generate_decision(claim, policy):

    prompt = f"""
You are an expert insurance claim analyst.

STRICT RULES:
- Return ONLY valid JSON
- No explanation outside JSON
- No markdown

Format:

{{
  "decision": "Approve / Reject / Partial / Conditional",
  "approved_amount": number,
  "confidence": number (0-100),
  "reasons": ["reason1", "reason2"],
  "explainability": "step-by-step reasoning"
}}

---

CLAIM:
{claim}

---

POLICY:
{policy}
"""

    response = call_llm([
        {"role": "system", "content": "Return strict JSON only."},
        {"role": "user", "content": prompt}
    ])

    data = extract_json(response)

    if not data:
        return {
            "decision": "Error",
            "approved_amount": 0,
            "confidence": 0,
            "reasons": ["Failed to parse LLM output"],
            "explainability": response
        }

    return data
