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
# 🎨 CLEAN UI
# -------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg,#f8fafc,#eef2f7);
}

.upload-box {
    background:white;
    padding:25px;
    border-radius:16px;
}

.card {
    background:white;
    padding:18px;
    border-radius:14px;
    text-align:center;
}

.kpi {
    background:white;
    padding:25px;
    border-radius:16px;
    text-align:center;
}

.pipeline {
    background:#111827;
    color:white;
    padding:12px;
    border-radius:10px;
    text-align:center;
}

.log-box {
    background:#f8fafc;
    padding:10px;
    border-radius:8px;
    font-size:14px;
    white-space:pre-wrap;
}

.success { color:#16a34a; }
.error { color:#dc2626; }
.warning { color:#f59e0b; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------
st.markdown("""
<div style="text-align:center; padding:20px;">
<h1>🛡️ AI Insurance Claim Intelligence</h1>
<p>AI + Rule Engine + Multi-Agent Decision System</p>
</div>
""", unsafe_allow_html=True)

# -------------------------
# PIPELINE
# -------------------------
pipeline_placeholder = st.empty()

def update_pipeline(step):
    pipeline_placeholder.markdown(f"""
    <div class="pipeline">{step}</div>
    """, unsafe_allow_html=True)

# -------------------------
# LOG FUNCTION
# -------------------------
def show_log(title, content):
    st.markdown(f"""
    <details>
    <summary><b>{title}</b></summary>
    <div class="log-box">{content}</div>
    </details>
    """, unsafe_allow_html=True)

# -------------------------
# UPLOAD
# -------------------------
st.markdown('<div class="upload-box">', unsafe_allow_html=True)
st.markdown("### 📂 Upload Documents")

col1, col2 = st.columns(2)

with col1:
    policy_file = st.file_uploader("Policy", type=["pdf"], label_visibility="collapsed")

with col2:
    claim_file = st.file_uploader("Claim", type=["pdf"], label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------
# MAIN FLOW
# -------------------------
if policy_file and claim_file:

    update_pipeline("📂 Upload Received")

    # -------------------------
    # EXTRACT
    # -------------------------
    update_pipeline("📄 Extracting Documents...")
    policy_text = extract_text(policy_file)
    claim_text = extract_text(claim_file)

    show_log("📄 Extract Agent", f"""
Policy:
{policy_text[:800]}

Claim:
{claim_text[:800]}
""")

    # -------------------------
    # RAG
    # -------------------------
    update_pipeline("📚 Retrieving Context...")
    store_policy(policy_text, policy_file.name)
    policy_context = get_policy_context(claim_text)

    show_log("📚 RAG Agent", policy_context[:800])

    # -------------------------
    # STRUCTURED EXTRACTION
    # -------------------------
    update_pipeline("🧠 Extracting Fields...")
    claim_data = extract_fields(claim_text, "claim")
    policy_data = extract_fields(policy_text, "policy")

    show_log("🧠 Extractor", f"""
Claim Data: {claim_data}
Policy Data: {policy_data}
""")

    # -------------------------
    # VALIDATION
    # -------------------------
    update_pipeline("🔍 Running Validation...")
    validation = validate_claim(claim_text, policy_text)

    show_log("🔍 Validation Agent", str(validation))

    # -------------------------
    # RULE ENGINE
    # -------------------------
    update_pipeline("📋 Applying Rules...")
    missing = check_mandatory_fields(claim_data, policy_data)
    date_check = check_policy_validity(claim_data, policy_data)

    show_log("📋 Rule Engine", f"""
Missing Fields: {missing}
Policy Validity: {date_check}
""")

    update_pipeline("✅ Processing Complete")

    # -------------------------
    # STATUS CARDS
    # -------------------------
    colA, colB, colC = st.columns(3)

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
            status = "✅ Active"; cls = "success"
        elif date_check["valid"] is False:
            status = "❌ Inactive"; cls = "error"
        else:
            status = "⚠️ Missing"; cls = "warning"

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
    # DECISION
    # -------------------------
    if st.button("🚀 Analyze Claim"):

        update_pipeline("🧠 Generating Decision...")
        result = generate_decision(claim_text, policy_context)

        show_log("🧠 Decision Agent", str(result))

        decision = result.get("decision","").upper()
        confidence = result.get("confidence",0)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"<div class='kpi'><h3>Decision</h3><h1>{decision}</h1></div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div class='kpi'><h3>Confidence</h3><h1>{confidence}%</h1></div>", unsafe_allow_html=True)

        update_pipeline("🔁 Reflection / Debate...")
        _, _, final = debate(claim_text, policy_context)

        show_log("🔁 Reflection Agent", final)

        update_pipeline("🏁 Final Decision Ready")

        if "approve" in final.lower():
            bg = "#ecfdf5"; border="#16a34a"
        elif "reject" in final.lower():
            bg = "#fef2f2"; border="#dc2626"
        else:
            bg = "#fffbeb"; border="#f59e0b"

        st.markdown(f"""
        <div style="
            background:{bg};
            padding:25px;
            border-radius:16px;
            border-left:6px solid {border};
        ">
        <h3>🏁 Final Decision</h3>
        {final}
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("👆 Upload documents to start")
