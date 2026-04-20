import streamlit as st
import sys, os

# Fix import paths (important for deployment)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports
from services.pdf_parser import extract_text
from services.rag import get_policy_context
from services.generator import generate_decision
from services.critic import critique
from services.reflection import improve
from services.debate import debate
from services.validator import validate_claim
from db.vectordb import store_policy

# ---------------- UI CONFIG ----------------
st.set_page_config(page_title="AI Insurance Claim Reviewer", layout="wide")

st.title("🛡️ AI Insurance Claim Reviewer")

# ---------------- POLICY UPLOAD ----------------
st.header("📄 Upload Policy")
policy_file = st.file_uploader("Upload Policy PDF", type=["pdf"], key="policy")

if policy_file:
    policy_text = extract_text(policy_file)
    store_policy(policy_text, policy_file.name)
    st.success("✅ Policy stored successfully!")

# ---------------- CLAIM UPLOAD ----------------
st.header("🧾 Upload Claim")
claim_file = st.file_uploader("Upload Claim PDF", type=["pdf"], key="claim")

if claim_file:

    # Step 1: Extract claim text
    claim_text = extract_text(claim_file)

    st.subheader("📌 Claim Extracted")
    st.write(claim_text[:500])

    # Step 2: Retrieve policy context (RAG)
    policy_context = get_policy_context(claim_text)

    st.subheader("📚 Policy Context")
    st.write(policy_context[:500])

    # ---------------- VALIDATION ----------------
    st.subheader("🔍 Validation Check")

    is_valid, messages = validate_claim(claim_text, policy_context)

    if not is_valid:
        st.error("❌ Validation Failed")
        for msg in messages:
            st.write(f"- {msg}")
        st.stop()
    else:
        st.success("✅ Validation Passed")

    # ---------------- PROCESS BUTTON ----------------
    if st.button("🚀 Process Claim"):

        # Step 3: Generator
        decision = generate_decision(claim_text, policy_context)
        st.subheader("🧠 Initial Decision")
        st.write(decision)

        # Step 4: Critic (Reflection)
        feedback = critique(decision)
        st.subheader("⚖️ Critic Feedback")
        st.write(feedback)

        # Step 5: Improve
        improved = improve(decision, feedback)
        st.subheader("🔁 Improved Decision")
        st.write(improved)

        # Step 6: Multi-Agent Debate
        approve, reject, final = debate(claim_text, policy_context)

        st.subheader("🧑‍💻 Approve Agent")
        st.write(approve)

        st.subheader("🧑‍⚖️ Reject Agent")
        st.write(reject)

        st.subheader("🏁 Final Decision")
        st.write(final)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("AI Insurance Claim System | RAG + Reflection + Validation + Multi-Agent Debate")
