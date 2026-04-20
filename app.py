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

st.set_page_config(page_title="AI Insurance Reviewer", layout="wide")

# -------------------------
# HEADER
# -------------------------
st.title("🛡️ AI Insurance Claim Reviewer")
st.markdown("### Intelligent Claim Processing with RAG + Reflection + Validation")

st.divider()

# -------------------------
# FILE UPLOAD SECTION
# -------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Upload Policy")
    policy_file = st.file_uploader("Policy PDF", type=["pdf"], key="policy")

with col2:
    st.subheader("🧾 Upload Claim")
    claim_file = st.file_uploader("Claim PDF", type=["pdf"], key="claim")

st.divider()

# -------------------------
# PROCESSING
# -------------------------
if policy_file and claim_file:

    with st.spinner("🔄 Processing documents..."):

        # Extract text
        policy_text = extract_text(policy_file)
        claim_text = extract_text(claim_file)

        if not policy_text or not claim_text:
            st.error("❌ Error reading PDF files")
            st.stop()

        # Store policy
        store_policy(policy_text, policy_file.name)

        # Layout
        colA, colB = st.columns(2)

        # -------------------------
        # LEFT SIDE (INPUTS)
        # -------------------------
        with colA:
            st.subheader("📌 Claim Details")
            st.info(claim_text[:600])

            st.subheader("📚 Policy Context (RAG)")
            policy_context = get_policy_context(claim_text)
            st.info(policy_context[:600])

        # -------------------------
        # RIGHT SIDE (VALIDATION + OUTPUT)
        # -------------------------
        with colB:

            st.subheader("🔍 Validation Check")

            validation_result = dynamic_validate(claim_text, policy_context)

            if not validation_result.get("valid", True):
                st.error("❌ Validation Failed")

                for issue in validation_result.get("issues", []):
                    st.write(f"⚠️ {issue}")

                st.stop()
            else:
                st.success("✅ Validation Passed")

        st.divider()

        # -------------------------
        # DECISION BUTTON
        # -------------------------
        if st.button("🚀 Analyze Claim", use_container_width=True):

            # Tabs for clean view
            tab1, tab2, tab3, tab4 = st.tabs([
                "🧠 Decision",
                "⚖️ Critic",
                "🔁 Improved",
                "🏁 Final"
            ])

            # Step 1: Decision
            with tab1:
                decision = generate_decision(claim_text, policy_context)
                st.write(decision)

            # Step 2: Critic
            with tab2:
                feedback = critique(decision)
                st.write(feedback)

            # Step 3: Improved
            with tab3:
                improved = improve(decision, feedback)
                st.write(improved)

            # Step 4: Debate
            with tab4:
                approve, reject, final = debate(claim_text, policy_context)

                colX, colY = st.columns(2)

                with colX:
                    st.markdown("### 🧑‍💻 Approve Agent")
                    st.write(approve)

                with colY:
                    st.markdown("### 🧑‍⚖️ Reject Agent")
                    st.write(reject)

                st.markdown("### 🏁 Final Decision")
                st.success(final)

        st.divider()

        # -------------------------
        # FEEDBACK
        # -------------------------
        st.subheader("⭐ Feedback")

        rating = st.slider("Rate the system output", 1, 5)

        if st.button("Submit Feedback"):
            st.success("✅ Feedback submitted!")

else:
    st.info("👆 Upload both Policy and Claim PDFs to begin")
