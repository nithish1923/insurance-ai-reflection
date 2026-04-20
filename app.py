import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.pdf_parser import extract_text
from db.vectordb import store_policy
from services.rag import get_policy_context
from services.generator import generate_decision
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
    background: linear-gradient(180deg, #f8fafc, #eef2f7);
}

/* Cards */
.card {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0px 6px 25px rgba(0,0,0,0.05);
    text-align:center;
}

/* KPI */
.kpi {
    text-align: center;
    padding: 25px;
    border-radius: 16px;
    background: white;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.05);
}

/* Button */
.stButton>button {
    width:100%;
    border-radius:12px;
    padding:12px;
    font-weight:600;
    background: linear-gradient(90deg, #4f46e5, #6366f1);
    color:white;
    border:none;
}

/* Status colors */
.success { color:#16a34a; font-weight:600; }
.error { color:#dc2626; font-weight:600; }
.warning { color:#f59e0b; font-weight:600; }

</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------
st.title("🛡️ AI Insurance Claim Intelligence")
st.caption("RAG • Validation • Rule Engine • Multi-Agent System")

st.divider()

# -------------------------
# UPLOAD
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

    with st.spinner("⚙️ Processing..."):

        policy_text = extract_text(policy_file)
        claim_text = extract_text(claim_file)

        store_policy(policy_text, policy_file.name)
        policy_context = get_policy_context(claim_text)

        # -------------------------
        # EXTRACT DATA
        # -------------------------
        claim_data = extract_fields(claim_text, "claim")
        policy_data = extract_fields(policy_text, "policy")

        # -------------------------
        # STATUS CARDS (SIDE BY SIDE)
        # -------------------------
        colA, colB, colC = st.columns(3)

        # Mandatory
        missing = check_mandatory_fields(claim_data, policy_data)
        with colA:
            if missing:
                st.markdown("""
                <div class="card">
                    <h4>📋 Mandatory</h4>
                    <p class="error">❌ Missing</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="card">
                    <h4>📋 Mandatory</h4>
                    <p class="success">✅ OK</p>
                </div>
                """, unsafe_allow_html=True)

        # Validation
        validation = validate_claim(claim_text, policy_text)
        with colB:
            if not validation.get("valid", True):
                st.markdown("""
                <div class="card">
                    <h4>🔍 Validation</h4>
                    <p class="error">❌ Failed</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="card">
                    <h4>🔍 Validation</h4>
                    <p class="success">✅ Passed</p>
                </div>
                """, unsafe_allow_html=True)

        # Policy Check
        date_check = check_policy_validity(claim_data, policy_data)
        with colC:
            if date_check["valid"] is False:
                st.markdown("""
                <div class="card">
                    <h4>📅 Policy</h4>
                    <p class="error">❌ Inactive</p>
                </div>
                """, unsafe_allow_html=True)
            elif date_check["valid"] is None:
                st.markdown("""
                <div class="card">
                    <h4>📅 Policy</h4>
                    <p class="warning">⚠️ Missing</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="card">
                    <h4>📅 Policy</h4>
                    <p class="success">✅ Active</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # STOP if invalid
        if missing or not validation.get("valid", True) or date_check["valid"] in [False, None]:
            st.stop()

        # -------------------------
        # ANALYZE BUTTON
        # -------------------------
        if st.button("🚀 Analyze Claim"):

            result = generate_decision(claim_text, policy_context)

            decision = result.get("decision", "N/A").upper()
            confidence = result.get("confidence", 0)

            # -------------------------
            # KPI STRIP
            # -------------------------
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div class="kpi">
                    <h3>🧠 Decision</h3>
                    <h1>{decision}</h1>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="kpi">
                    <h3>📊 Confidence</h3>
                    <h1>{confidence}%</h1>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # -------------------------
            # FINAL DECISION (FIXED)
            # -------------------------
            approve, reject, final = debate(claim_text, policy_context)
            final_lower = final.lower()

            if "final decision: approve" in final_lower:
                bg = "#ecfdf5"
                border = "#16a34a"
            elif "final decision: reject" in final_lower:
                bg = "#fef2f2"
                border = "#dc2626"
            else:
                bg = "#fffbeb"
                border = "#f59e0b"

            st.markdown(f"""
            <div style="
                background:{bg};
                padding:25px;
                border-radius:16px;
                border-left:6px solid {border};
                box-shadow:0px 4px 20px rgba(0,0,0,0.05);
            ">
            <h3>🏁 Final Decision</h3>
            <p>{final}</p>
            </div>
            """, unsafe_allow_html=True)

            # -------------------------
            # REPORT
            # -------------------------
            report = f"""
Decision: {decision}
Confidence: {confidence}
Final: {final}
"""
            st.download_button("📥 Download Report", report)

else:
    st.info("👆 Upload Policy and Claim PDFs to begin")
