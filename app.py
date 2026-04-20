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

st.set_page_config(page_title="AI Insurance AI", layout="wide")

# -------------------------
# CUSTOM STYLING
# -------------------------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
.card {
    padding: 20px;
    border-radius: 12px;
    background-color: #1c1f26;
    margin-bottom: 15px;
}
.success-box {
    background-color: #0f5132;
    padding: 10px;
    border-radius: 8px;
}
.error-box {
    background-color: #842029;
    padding: 10px;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------
st.title("🛡️ AI Insurance Claim Intelligence")
st.caption("RAG • Validation • Reflection • Multi-Agent Decision System")

st.divider()

# -------------------------
# UPLOAD SECTION
# -------------------------
col1, col2 = st.columns(2)

with col1:
    policy_file = st.file_uploader("📄 Upload Policy", type=["pdf"])

with col2:
    claim_file = st.file_uploader("🧾 Upload Claim", type=["pdf"])

st.divider()

# -------------------------
# MAIN PROCESS
# -------------------------
if policy_file and claim_file:

    with st.spinner("⚙️ Analyzing documents..."):

        policy_text = extract_text(policy_file)
        claim_text = extract_text(claim_file)

        store_policy(policy_text, policy_file.name)
        policy_context = get_policy_context(claim_text)

        # -------------------------
        # INPUT VIEW
        # -------------------------
        colA, colB = st.columns(2)

        with colA:
            st.markdown("### 📌 Claim")
            st.code(claim_text[:600])

        with colB:
            st.markdown("### 📚 Policy Context")
            st.code(policy_context[:600])

        st.divider()

        # -------------------------
        # VALIDATION
        # -------------------------
        st.markdown("## 🔍 Validation Engine")

        validation = dynamic_validate(claim_text, policy_context)

        if not validation.get("valid", True):
            st.markdown('<div class="error-box">❌ Validation Failed</div>', unsafe_allow_html=True)
            for issue in validation.get("issues", []):
                st.write(f"⚠️ {issue}")
            st.stop()
        else:
            st.markdown('<div class="success-box">✅ Validation Passed</div>', unsafe_allow_html=True)

        st.divider()

        # -------------------------
        # ANALYZE BUTTON
        # -------------------------
        if st.button("🚀 Run AI Analysis", use_container_width=True):

            # Decision
            decision = generate_decision(claim_text, policy_context)

            # Risk scoring (simple logic)
            risk_score = 30 if "approve" in decision.lower() else 75

            # -------------------------
            # RESULT HEADER
            # -------------------------
            st.markdown("## 🧠 Decision Summary")

            colX, colY = st.columns([2,1])

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
            # TABS (CLEAN VIEW)
            # -------------------------
            tab1, tab2, tab3, tab4 = st.tabs([
                "⚖️ Critic",
                "🔁 Improved",
                "🤖 Debate",
                "📄 Report"
            ])

            with tab1:
                feedback = critique(decision)
                st.write(feedback)

            with tab2:
                improved = improve(decision, feedback)
                st.write(improved)

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
        st.markdown("## ⭐ Feedback")

        rating = st.slider("Rate system performance", 1, 5)

        if st.button("Submit Feedback"):
            st.success("Thanks for your feedback!")

else:
    st.info("👆 Upload both Policy and Claim to start")
