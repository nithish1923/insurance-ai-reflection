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
# 🎨 PREMIUM UI STYLE
# -------------------------
st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

.badge {
    padding: 6px 12px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
}

.approve { background-color: #eafaf1; color: #27ae60; }
.reject { background-color: #fdecea; color: #e74c3c; }
.conditional { background-color: #fff8e1; color: #f39c12; }

.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

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

        policy_text = extract_text(policy_file)
        claim_text = extract_text(claim_file)

        if not policy_text or not claim_text:
            st.error("❌ Error reading PDF")
            st.stop()

        store_policy(policy_text, policy_file.name)
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
        # EXTRACT DATA
        # -------------------------
        claim_data = extract_fields(claim_text, "claim")
        policy_data = extract_fields(policy_text, "policy")

        # -------------------------
        # MANDATORY CHECK
        # -------------------------
        st.subheader("📋 Mandatory Field Check")

        missing = check_mandatory_fields(claim_data, policy_data)

        if missing:
            st.error("❌ Missing Required Fields")
            for m in missing:
                st.write(f"⚠️ {m}")
            st.stop()
        else:
            st.success("✅ All mandatory fields present")

        st.divider()

        # -------------------------
        # VALIDATION
        # -------------------------
        st.subheader("🔍 Validation Engine")

        validation = validate_claim(claim_text, policy_text)

        if not validation.get("valid", True):
            st.error("❌ Validation Failed")
            for issue in validation.get("issues", []):
                st.write(f"⚠️ {issue}")
            st.stop()
        else:
            st.success("✅ Validation Passed")

        st.divider()

        # -------------------------
        # DATE RULE ENGINE
        # -------------------------
        st.subheader("📅 Policy Validity Check")

        date_check = check_policy_validity(claim_data, policy_data)

        if date_check["valid"] is False:
            st.error("❌ Policy Not Active")
            st.write(date_check["reason"])
            st.stop()

        elif date_check["valid"] is None:
            st.error("❌ Cannot Process Claim")
            st.write("⚠️ Missing Incident Date")
            st.stop()

        else:
            st.success("✅ Policy Active")

        st.divider()

        # -------------------------
        # ANALYSIS
        # -------------------------
        if st.button("🚀 Analyze Claim", use_container_width=True):

            result = generate_decision(claim_text, policy_context)

            decision = result.get("decision", "N/A").lower()
            confidence = result.get("confidence", 0)

            if "approve" in decision:
                badge = "approve"
                icon = "✅"
            elif "reject" in decision:
                badge = "reject"
                icon = "❌"
            else:
                badge = "conditional"
                icon = "⚠️"

            # -------------------------
            # DECISION CARD
            # -------------------------
            st.markdown(f"""
            <div class="card">
                <div class="section-title">🧠 Decision Summary</div>
                <span class="badge {badge}">
                    {icon} {decision.upper()}
                </span>
                <br><br>
                <b>Confidence:</b> {confidence}%
            </div>
            """, unsafe_allow_html=True)

            # -------------------------
            # BREAKDOWN
            # -------------------------
            st.markdown('<div class="card"><div class="section-title">📊 Decision Breakdown</div>', unsafe_allow_html=True)

            for r in result.get("reasons", []):
                st.markdown(f"✔️ {r}")

            st.markdown("</div>", unsafe_allow_html=True)

            # -------------------------
            # EXPLAINABILITY
            # -------------------------
            st.markdown(f"""
            <div class="card">
                <div class="section-title">🧠 Explainability</div>
                {result.get("explainability", "")}
            </div>
            """, unsafe_allow_html=True)

            # -------------------------
            # FINAL DECISION
            # -------------------------
            approve, reject, final = debate(claim_text, policy_context)

            if "reject" in final.lower():
                color = "#fdecea"
                border = "#e74c3c"
            else:
                color = "#eafaf1"
                border = "#2ecc71"

            st.markdown(f"""
            <div style="
                background:{color};
                padding:20px;
                border-radius:12px;
                border-left:6px solid {border};
                margin-top:20px;
            ">
            <b>🏁 Final Decision</b><br><br>
            {final}
            </div>
            """, unsafe_allow_html=True)

            # -------------------------
            # REPORT
            # -------------------------
            report = f"""
Decision: {decision}
Confidence: {confidence}
Reasons: {result.get("reasons")}
Explainability: {result.get("explainability")}
Final: {final}
"""
            st.download_button("📥 Download Report", report)

        st.divider()

else:
    st.info("👆 Upload both Policy and Claim PDFs to begin")
