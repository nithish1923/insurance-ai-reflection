from services.llm import call_llm
import json

def dynamic_validate(claim_text, policy_text):

    prompt = f"""
You are an insurance validation engine.

Compare CLAIM and POLICY carefully.

STRICT RULES:
- Do NOT assume anything
- Only use given text
- Detect mismatches such as:
  - Name mismatch
  - Policy number mismatch
  - Vehicle mismatch
  - Missing required info

Return ONLY valid JSON (no extra text):

{{
  "valid": true/false,
  "issues": ["issue1", "issue2"]
}}

-------------------

CLAIM:
{claim_text}

-------------------

POLICY:
{policy_text}
"""

    response = call_llm([
        {"role": "system", "content": "You are a strict validation engine."},
        {"role": "user", "content": prompt}
    ])

    # Clean parsing (important)
    try:
        return json.loads(response)
    except:
        return {
            "valid": True,
            "issues": ["⚠️ Could not parse validation output"]
        }
