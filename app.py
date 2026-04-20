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
# 🎨 PREMIUM GLOBAL STYLE
# -------------------------
st.markdown("""
<style>

/* Page background */
.main {
    background: linear-gradient(180deg, #f8fafc, #eef2f7);
}

/* Hero */
.hero {
    text-align: center;
    padding: 30px 0px;
}

.hero-title {
    font-size: 38px;
    font-weight: 700;
}

.hero-sub {
    font-size: 16px;
    color: #6b7280;
}

/* Badge */
.badge {
    display: inline-block;
    background: #eef2ff;
    color: #4f46e5;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
    margin-top: 10px;
}

/* Upload box */
.upload-box {
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0px 6px 25px rgba(0,0,0,0.05);
}

/* File info */
.file-info {
    background: #f1f5f9;
    padding: 10px;
    border-radius: 8px;
    margin-top: 8px;
    font-size: 14px;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.9);
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
    text-align:center;
}

/* KPI */
.kpi {
    padding: 25px;
    border-radius: 16px;
    background: white;
    text-align:center;
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
}

/* Colors */
.success { color:#16a34a; font-weight:600; }
.error { color:#dc2626; font-weight:600; }
.warning { color:#f59e0b; font-weight:600; }

</style>
""", unsafe_allow_html=True)

# -------------------------
# 🌟 HERO HEADER
# -------------------------
st.markdown("""
<div class="hero">
    <div class="hero-title">🛡️ AI Insurance Claim Intelligence</div>
    <div class="hero-sub">
        Automated claim validation using AI + Rule Engine + Multi-Agent reasoning
    </div>
    <div class="badge">Production AI System</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------
# 📂 UPLOAD SECTION
# -------------------------
st.markdown('<div class="upload-box">', unsafe_allow_html=True)

st.markdown("### 📂 Upload Documents")

col1, col2 = st.columns(2)

with col1:
    policy_file = st.file_uploader("Policy", type=["pdf"], label_visibility="collapsed")

    if policy_file:
        st.markdown(f"""
        <div class="file-info">
        📄 {policy_file.name}<br>
        📦 {round(policy_file.size/1024,2)} KB
        </div>
        """, unsafe_allow_html=True)

with col2:
    claim_file = st.file_uploader("Claim", type=["pdf"], label_visibility="collapsed")

    if claim_file:
        st.markdown(f"""
        <div class="file-info">
        🧾 {claim_file.name}<br>
        📦 {round(claim_file.size/1024,2)} KB
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------
# MAIN FLOW
# -------------------------
if policy_file and claim_file:

    policy_text = extract_text(policy_file)
    claim_text = extract_text(claim_file)

    store_policy(policy_text, policy_file.name)
    policy_context = get_policy_context(claim_text)

    claim_data = extract_fields(claim_text, "claim")
    policy_data = extract_fields(policy_text, "policy")

    # -------------------------
    # STATUS CARDS
    # -------------------------
    colA, colB, colC = st.columns(3)

    missing = check_mandatory_fields(claim_data, policy_data)
    validation = validate_claim(claim_text, policy_text)
    date_check = check_policy_validity(claim_data, policy_data)

    with colA:
        st.markdown(f"""
        <div class="card">
        <b>📋 Mandatory</b><br><br>
        <span class="{'error' if missing else 'success'}">
        {'❌ Missing' if missing else '✅ OK'}
        </span>
        </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown(f"""
        <div class="card">
        <b>🔍 Validation</b><br><br>
        <span class="{'error' if not validation.get('valid',True) else 'success'}">
        {'❌ Failed' if not validation.get('valid',True) else '✅ Passed'}
        </span>
        </div>
        """, unsafe_allow_html=True)

    with colC:
        if date_check["valid"] is True:
            status = "✅ Active"
            cls = "success"
        elif date_check["valid"] is False:
            status = "❌ Inactive"
            cls = "error"
        else:
            status = "⚠️ Missing"
            cls = "warning"

        st.markdown(f"""
        <div class="card">
        <b>📅 Policy</b><br><br>
        <span class="{cls}">{status}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if missing or not validation.get("valid", True) or date_check["valid"] != True:
        st.stop()

    # -------------------------
    # ANALYZE
    # -------------------------
    if st.button("🚀 Analyze Claim"):

        result = generate_decision(claim_text, policy_context)
        decision = result.get("decision","").upper()
        confidence = result.get("confidence",0)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"<div class='kpi'><h3>Decision</h3><h1>{decision}</h1></div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div class='kpi'><h3>Confidence</h3><h1>{confidence}%</h1></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # FINAL DECISION
        _, _, final = debate(claim_text, policy_context)

        if "final decision: approve" in final.lower():
            bg = "#ecfdf5"; border="#16a34a"
        elif "final decision: reject" in final.lower():
            bg = "#fef2f2"; border="#dc2626"
        else:
            bg = "#fffbeb"; border="#f59e0b"

        st.markdown(f"""
        <div style="
            background:{bg};
            padding:25px;
            border-radius:16px;
            border-left:6px solid {border};
            box-shadow:0px 4px 20px rgba(0,0,0,0.05);
        ">
        <h3>🏁 Final Decision</h3>
        {final}
        </div>
        """, unsafe_allow_html=True)

        st.download_button("📥 Download Report", final)

else:
    st.info("👆 Upload documents to start analysis")
