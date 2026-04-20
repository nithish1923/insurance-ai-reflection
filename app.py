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
# 🌙 DARK MODE TOGGLE
# -------------------------
st.sidebar.markdown("### ⚙️ Settings")
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)

# -------------------------
# 🎨 DYNAMIC STYLES
# -------------------------
if dark_mode:
    st.markdown("""
    <style>
    .main { background:#0f172a; color:#e2e8f0; }

    .hero-title { color:#f8fafc; font-size:36px; font-weight:700; }
    .hero-sub { color:#94a3b8; }

    .upload-box { background:#1e293b; padding:25px; border-radius:16px; }
    .file-info { background:#334155; padding:10px; border-radius:8px; }

    .card { background:#1e293b; padding:18px; border-radius:14px; text-align:center; }
    .kpi { background:#1e293b; padding:25px; border-radius:16px; text-align:center; }

    .stButton>button {
        background: linear-gradient(90deg,#6366f1,#8b5cf6);
        color:white; border-radius:12px;
    }

    .success { color:#22c55e; }
    .error { color:#ef4444; }
    .warning { color:#facc15; }
    </style>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <style>
    .main { background:linear-gradient(180deg,#f8fafc,#eef2f7); }

    .hero-title { color:#111827; font-size:36px; font-weight:700; }
    .hero-sub { color:#6b7280; }

    .upload-box { background:white; padding:25px; border-radius:16px; }
    .file-info { background:#f1f5f9; padding:10px; border-radius:8px; }

    .card { background:white; padding:18px; border-radius:14px; text-align:center; }
    .kpi { background:white; padding:25px; border-radius:16px; text-align:center; }

    .stButton>button {
        background: linear-gradient(90deg,#4f46e5,#6366f1);
        color:white; border-radius:12px;
    }

    .success { color:#16a34a; }
    .error { color:#dc2626; }
    .warning { color:#f59e0b; }
    </style>
    """, unsafe_allow_html=True)

# -------------------------
# 🌟 HERO HEADER
# -------------------------
st.markdown("""
<div style="text-align:center; padding:20px;">
    <div class="hero-title">🛡️ AI Insurance Claim Intelligence</div>
    <div class="hero-sub">
        AI + Rule Engine + Multi-Agent Claim Decision System
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------
# 📂 UPLOAD UI
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

st.markdown("</div>", unsafe_allow_html=True)

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

    # STOP if invalid
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
    st.info("👆 Upload documents to start")
