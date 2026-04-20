import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.pdf_parser import extract_text
from db.vectordb import store_policy
from services.rag import get_policy_context
from services.generator import generate_decision
from services.critic import critique
from services.reflection import improve
from services.debate import debate
from services.validator import dynamic_validate

st.set_page_config(page_title="AI Insurance Claim Reviewer", layout="wide")

st.title("🛡️ AI Insurance Claim Reviewer")

# -------------------------
# Upload Policy
# -------------------------
st.header("📄 Upload Policy")
policy_file = st.file_uploader("Upload Policy PDF", type=["pdf"])

if policy_file:
    policy_text = extract_text(policy_file)

    if not policy_text:
        st.error("❌ Could not read policy PDF")
    else:
        store_policy(policy_text, policy_file.name)
        st.success("✅ Policy stored successfully!")

# -------------------------
# Upload Claim
# -------------------------
st.header("🧾 Upload Claim")
claim_file = st.file_uploader("Upload Claim PDF", type=["pdf"])

if claim_file:
    claim_text = extract_text(claim_file)

    if not claim_text:
        st.error("❌ Could not read claim PDF")
        st.stop()

    st.subheader("📌 Claim Extracted")
    st.write(claim_text[:500])

    # -------------------------
    # RAG Retrieval
    # -------------------------
    policy_context = get_policy_context(claim_text)

    st.subheader("📚 Policy Context")
    st.write(policy_context[:500])

    # -------------------------
    # Dynamic Validation (AI)
    # -------------------------
    st.subheader("🔍 Validation Result")

    validation_result = dynamic_validate(claim_text, policy_context)

    if not validation_result.get("valid", True):
        st.error("❌ Validation Failed")

        for issue in validation_result.get("issues", []):
            st.write(f"- {issue}")

        st.stop()
    else:
        st.success("✅ Validation Passed")

    # -------------------------
    # Process Claim
    # -------------------------
    if st.button("🚀 Process Claim"):

        # Step 1: Generate Decision
        decision = generate_decision(claim_text, policy_context)
        st.subheader("🧠 Initial Decision")
        st.write(decision)

        # Step 2: Critic Feedback
        feedback = critique(decision)
        st.subheader("⚖️ Critic Feedback")
        st.write(feedback)

        # Step 3: Improve Decision
        improved = improve(decision, feedback)
        st.subheader("🔁 Improved Decision")
        st.write(improved)

        # Step 4: Multi-Agent Debate
        approve, reject, final = debate(claim_text, policy_context)

        st.subheader("🧑‍💻 Approve Agent")
        st.write(approve)

        st.subheader("🧑‍⚖️ Reject Agent")
        st.write(reject)

        st.subheader("🏁 Final Decision (Judge)")
        st.write(final)

        # -------------------------
        # Feedback System
        # -------------------------
        rating = st.slider("⭐ Rate Decision", 1, 5)

        if st.button("Submit Feedback"):
            st.success("✅ Feedback recorded!")
