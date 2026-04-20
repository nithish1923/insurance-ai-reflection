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
from services.validator import validate_claim

st.set_page_config(page_title="AI Insurance Intelligence", layout="wide")

# -------------------------
# HEADER
# -------------------------
st.title("🛡️ AI Insurance Claim Intelligence")
st.caption("RAG • Validation • Reflection • Multi-Agent Decision System")

st.divider()

# -------------------------
# FILE UPLOAD
# -------------------------
col1, col2 = st.columns(2)

with col1:
    policy_file = st.file_uploader("📄 Upload Policy", type=["pdf"])

with col2:
    claim_file = st.file_uploader("🧾 Upload Claim", type=["pdf"])

st.divider()

# -------------------------
# MAIN FLOW
# -------------------------
if policy_file and claim_file:

    with st.spinner("⚙️ Processing documents..."):

        # Extract text
        policy_text = extract_text(policy_file)
        claim_text = extract_text(claim_file)

        if not policy_text or not claim_text:
            st.error("❌ Error reading PDF")
            st.stop()

        # Store policy for RAG
        store_policy(policy_text, policy_file.name)

        # Get RAG context
        policy_context = get_policy_context(claim_text)

        # -------------------------
        # DISPLAY INPUTS
        # -------------------------
        colA, colB = st.columns(2)

        with colA:
            st.subheader("📌 Claim")
            st.code(claim_text[:600])

        with colB:
            st.subheader("📚 Policy Context (RAG)")
            st.code(policy_context[:600])

        st.divider()

        # -------------------------
        # VALIDATION (STRUCTURED)
        # -------------------------
        st.subheader("🔍 Validation Engine")

        validation_result = validate_claim(claim_text, policy_text)

        if not validation_result.get("valid", True):
            st.error("❌ Validation Failed")

            for issue in validation_result.get("issues", []):
                st.write(f"⚠️ {issue}")

            st.stop()
        else:
            st.success("✅ Validation Passed")

        st.divider()

        # -------------------------
        # ANALYSIS BUTTON
        # -------------------------
        if st.button("🚀 Analyze Claim", use_container_width=True):

            # Step 1: Decision
            decision = generate_decision(claim_text, policy_context)

            # Risk score (simple heuristic)
            risk_score = 30 if "approve" in decision.lower() else 75

            # -------------------------
            # DECISION SUMMARY
            # -------------------------
            st.subheader("🧠 Decision Summary")

            colX, colY = st.columns([2, 1])

            with colX:
                if "approve" in decision.lower():
                    st.success("✅ APPROVED")
                elif "reject" in decision.lower():
                    st.error("❌ REJECTED")
                else:
                    st.warning("⚠️ CONDITIONAL")

                st.write(decision)

            with colY:
                st.metric("Risk Score", f"{risk_score}%")
                st.progress(risk_score / 100)

            st.divider()

            # -------------------------
            # TABS
            # -------------------------
            tab1, tab2, tab3, tab4 = st.tabs([
                "⚖️ Critic",
                "🔁 Improved",
                "🤖 Debate",
                "📄 Report"
            ])

            # Critic
            with tab1:
                feedback = critique(decision)
                st.write(feedback)

            # Improved
            with tab2:
                improved = improve(decision, feedback)
                st.write(improved)

            # Debate
            with tab3:
                approve, reject, final = debate(claim_text, policy_context)

                colL, colR = st.columns(2)

                with colL:
                    st.markdown("### 👍 Approve Agent")
                    st.write(approve)

                with colR:
                    st.markdown("### 👎 Reject Agent")
                    st.write(reject)

                st.markdown("### 🏁 Final Decision")
                st.success(final)

            # Report
            with tab4:
                report = f"""
AI Insurance Claim Report

Decision:
{decision}

Critic:
{feedback}

Improved:
{improved}

Final:
{final}
"""
                st.download_button("📥 Download Report", report)

        st.divider()

        # -------------------------
        # FEEDBACK
        # -------------------------
        st.subheader("⭐ Feedback")

        rating = st.slider("Rate system output", 1, 5)

        if st.button("Submit Feedback"):
            st.success("✅ Feedback recorded!")

else:
    st.info("👆 Upload both Policy and Claim PDFs to begin")
