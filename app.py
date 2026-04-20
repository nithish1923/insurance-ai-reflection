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
from services.extractor import extract_fields
from services.rules import check_policy_validity
from services.validation_rules import check_mandatory_fields

st.set_page_config(page_title="AI Insurance Intelligence", layout="wide")

# -------------------------
# HEADER
# -------------------------
st.title("🛡️ AI Insurance Claim Intelligence")
st.caption("RAG • Validation • Rule Engine • Multi-Agent System")

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
        # EXTRACT STRUCTURED DATA
        # -------------------------
        claim_data = extract_fields(claim_text, "claim")
        policy_data = extract_fields(policy_text, "policy")

        # DEBUG (optional)
        # st.json(claim_data)
        # st.json(policy_data)

        # -------------------------
        # MANDATORY FIELD CHECK
        # -------------------------
        st.subheader("📋 Mandatory Field Check")

        missing_fields = check_mandatory_fields(claim_data, policy_data)

        if missing_fields:
            st.error("❌ Missing Required Fields")
            for field in missing_fields:
                st.write(f"⚠️ {field}")
            st.stop()
        else:
            st.success("✅ All mandatory fields present")

        st.divider()

        # -------------------------
        # VALIDATION
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
        # DATE RULE ENGINE (STRICT FIX)
        # -------------------------
        st.subheader("📅 Policy Validity Check")

        date_check = check_policy_validity(claim_data, policy_data)

        if date_check["valid"] is False:
            st.error("❌ Policy Not Active")
            st.write(date_check["reason"])
            st.stop()

        elif date_check["valid"] is None:
            st.error("❌ Cannot Process Claim")
            st.write("⚠️ Missing Incident Date in claim")
            st.stop()   # 🚨 CRITICAL FIX

        else:
            st.success("✅ Policy Active for Incident")

        st.divider()

        # -------------------------
        # ANALYSIS
        # -------------------------
        if st.button("🚀 Analyze Claim", use_container_width=True):

            result = generate_decision(claim_text, policy_context)

            st.subheader("🧠 Decision Summary")

            col1, col2 = st.columns(2)

            with col1:
                decision = result.get("decision", "N/A")

                if decision.lower() == "approve":
                    st.success(f"✅ {decision}")
                elif decision.lower() == "reject":
                    st.error(f"❌ {decision}")
                else:
                    st.warning(f"⚠️ {decision}")

            with col2:
                st.metric("Confidence", f"{result.get('confidence', 0)}%")

            st.divider()

            # -------------------------
            # BREAKDOWN
            # -------------------------
            st.subheader("📊 Decision Breakdown")

            for r in result.get("reasons", []):
                st.write(f"✔️ {r}")

            st.divider()

            # -------------------------
            # EXPLAINABILITY
            # -------------------------
            st.subheader("🧠 Explainability")
            st.info(result.get("explainability", ""))

            st.divider()

            # -------------------------
            # REFLECTION
            # -------------------------
            tab1, tab2, tab3 = st.tabs([
                "⚖️ Critic",
                "🔁 Improved",
                "🤖 Debate"
            ])

            with tab1:
                feedback = critique(str(result))
                st.write(feedback)

            with tab2:
                improved = improve(str(result), feedback)
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

            st.divider()

            # -------------------------
            # REPORT DOWNLOAD
            # -------------------------
            report = f"""
AI Insurance Claim Report

Decision:
{result.get("decision")}

Confidence:
{result.get("confidence")}

Reasons:
{result.get("reasons")}

Explainability:
{result.get("explainability")}
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
