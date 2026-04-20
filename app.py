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
.card {
    background: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
    text-align: center;
}

/* Status Colors */
.success { color: #27ae60; font-weight:600; }
.error { color: #e74c3c; font-weight:600; }
.warning { color: #f39c12; font-weight:600; }

.badge {
    padding: 6px 12px;
    border-radius: 8px;
    font-weight: 600;
}

.approve { background:#eafaf1; color:#27ae60; }
.reject { background:#fdecea; color:#e74c3c; }
.conditional { background:#fff8e1; color:#f39c12; }
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
        # 🧠 STATUS CARDS (SIDE BY SIDE)
        # -------------------------
        colA, colB, colC = st.columns(3)

        # -------- Mandatory --------
        with colA:
            missing = check_mandatory_fields(claim_data, policy_data)

            if missing:
                st.markdown(f"""
                <div class="card">
                    <b>📋 Mandatory Check</b><br><br>
                    <span class="error">❌ Missing</span>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                <div class="card">
                    <b>📋 Mandatory Check</b><br><br>
                    <span class="success">✅ OK</span>
                </div>
                """, unsafe_allow_html=True)

        # -------- Validation --------
        with colB:
            validation = validate_claim(claim_text, policy_text)

            if not validation.get("valid", True):
                st.markdown(f"""
                <div class="card">
                    <b>🔍 Validation</b><br><br>
                    <span class="error">❌ Failed</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="card">
                    <b>🔍 Validation</b><br><br>
                    <span class="success">✅ Passed</span>
                </div>
                """, unsafe_allow_html=True)

        # -------- Date Check --------
        with colC:
            date_check = check_policy_validity(claim_data, policy_data)

            if date_check["valid"] is False:
                st.markdown(f"""
                <div class="card">
                    <b>📅 Policy Check</b><br><br>
                    <span class="error">❌ Inactive</span>
                </div>
                """, unsafe_allow_html=True)

            elif date_check["valid"] is None:
                st.markdown(f"""
                <div class="card">
                    <b>📅 Policy Check</b><br><br>
                    <span class="warning">⚠️ Missing Date</span>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                <div class="card">
                    <b>📅 Policy Check</b><br><br>
                    <span class="success">✅ Active</span>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # 🚫 STOP if issues
        if missing or not validation.get("valid", True) or date_check["valid"] is None or date_check["valid"] is False:
            st.stop()

        # -------------------------
        # ANALYZE
        # -------------------------
        if st.button("🚀 Analyze Claim", use_container_width=True):

            result = generate_decision(claim_text, policy_context)

            decision = result.get("decision", "").lower()
            confidence = result.get("confidence", 0)

            # Badge
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
                <b>🧠 Decision</b><br><br>
                <span class="badge {badge}">
                    {icon} {decision.upper()}
                </span><br><br>
                Confidence: {confidence}%
            </div>
            """, unsafe_allow_html=True)

            # -------------------------
            # FINAL DECISION FIXED
            # -------------------------
            approve, reject, final = debate(claim_text, policy_context)
            final_lower = final.lower()

            if "final decision: approve" in final_lower:
                color = "#eafaf1"
                border = "#2ecc71"
                icon = "✅"
            elif "final decision: reject" in final_lower:
                color = "#fdecea"
                border = "#e74c3c"
                icon = "❌"
            else:
                color = "#fff8e1"
                border = "#f39c12"
                icon = "⚠️"

            st.markdown(f"""
            <div style="
                background:{color};
                padding:20px;
                border-radius:12px;
                border-left:6px solid {border};
                margin-top:20px;
            ">
            <b>{icon} Final Decision</b><br><br>
            {final}
            </div>
            """, unsafe_allow_html=True)

else:
    st.info("👆 Upload both Policy and Claim PDFs")
