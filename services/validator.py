from services.llm import call_llm
import json

def dynamic_validate(claim_text, policy_text):

    prompt = f"""
You are an insurance validation engine.

Your job:
Compare CLAIM and POLICY carefully and identify ONLY clear mismatches.

STRICT RULES:
- Do NOT guess or assume
- Only flag mismatches if explicitly different
- If data is missing → DO NOT mark as mismatch
- Be conservative (avoid false positives)

Check only:
1. Name mismatch (if both names clearly present)
2. Policy number mismatch (if both present)
3. Vehicle mismatch (if clearly different)

Return ONLY JSON:

{{
  "valid": true/false,
  "issues": []
}}

---

CLAIM:
{claim_text}

---

POLICY:
{policy_text}
"""

    response = call_llm([
        {"role": "system", "content": "You are a strict but accurate validator."},
        {"role": "user", "content": prompt}
    ])

    try:
        return json.loads(response)
    except:
        return {
            "valid": True,
            "issues": ["⚠️ Validation parsing failed"]
        }
