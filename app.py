import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
from services.validator import validate_claim
from services.pdf_parser import extract_text
from db.vectordb import store_policy
from services.rag import get_policy_context
from services.generator import generate_decision
from services.critic import critique
from services.reflection import improve
from services.debate import debate

st.set_page_config(page_title="AI Insurance Reviewer", layout="wide")

st.title("🛡️ AI Insurance Claim Reviewer")

# Upload Policy
st.header("📄 Upload Policy")
policy_file = st.file_uploader("Upload Policy PDF", type=["pdf"])

if policy_file:
    text = extract_text(policy_file)
    store_policy(text, policy_file.name)
    st.success("Policy stored successfully!")

# Upload Claim
st.header("🧾 Upload Claim")
claim_file = st.file_uploader("Upload Claim PDF", type=["pdf"])

if claim_file:
    claim_text = extract_text(claim_file)

    st.subheader("📌 Claim Extracted")
    st.write(claim_text[:500])

    policy_context = get_policy_context(claim_text)

    # -------- VALIDATION STEP --------
is_valid, messages = validate_claim(claim_text, policy_context)

if not is_valid:
    st.error("❌ Validation Failed")
    for msg in messages:
        st.write(f"- {msg}")
    st.stop()
else:
    st.success("✅ Validation Passed")

    st.subheader("📚 Policy Context")
    st.write(policy_context[:500])

    if st.button("🚀 Process Claim"):

        decision = generate_decision(claim_text, policy_context)
        st.subheader("🧠 Initial Decision")
        st.write(decision)

        feedback = critique(decision)
        st.subheader("⚖️ Critic Feedback")
        st.write(feedback)

        improved = improve(decision, feedback)
        st.subheader("🔁 Improved Decision")
        st.write(improved)

        approve, reject, final = debate(claim_text, policy_context)

        st.subheader("🧑‍💻 Approve Agent")
        st.write(approve)

        st.subheader("🧑‍⚖️ Reject Agent")
        st.write(reject)

        st.subheader("🏁 Final Decision")
        st.write(final)
