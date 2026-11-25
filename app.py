import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Water Quality Predictor",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .result-yes {
        background-color: #e6f4ea; border-left: 8px solid #1e8e3e;
        padding: 20px; border-radius: 10px; color: #137333;
    }
    .result-no {
        background-color: #fce8e6; border-left: 8px solid #d93025;
        padding: 20px; border-radius: 10px; color: #c5221f;
    }
    .big-verdict { font-size: 32px; font-weight: 800; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Safe limits (no dataset or model files needed)
#    (label, min allowed, max allowed)
# -----------------------------------------------------------------------------
LIMITS = {
    "ph":              ("pH",                    6.5,  8.5),
    "Hardness":        ("Hardness (mg/L)",       0.0,  300.0),
    "Solids":          ("Dissolved Solids (ppm)", 0.0, 1000.0),
    "Chloramines":     ("Chloramines (ppm)",     0.0,  4.0),
    "Sulfate":         ("Sulfate (mg/L)",        0.0,  250.0),
    "Conductivity":    ("Conductivity (μS/cm)",  0.0,  400.0),
    "Organic_carbon":  ("Organic Carbon (ppm)",  0.0,  4.0),
    "Trihalomethanes": ("Trihalomethanes (μg/L)", 0.0, 80.0),
    "Turbidity":       ("Turbidity (NTU)",       0.0,  5.0),
}

presets = {
    "median": {
        "ph": 7.04, "Hardness": 196.97, "Solids": 20927.83,
        "Chloramines": 7.13, "Sulfate": 333.07, "Conductivity": 421.88,
        "Organic_carbon": 14.22, "Trihalomethanes": 66.62, "Turbidity": 3.96,
    },
    "clean": {
        "ph": 7.20, "Hardness": 150.00, "Solids": 500.00,
        "Chloramines": 3.50, "Sulfate": 200.00, "Conductivity": 350.00,
        "Organic_carbon": 3.00, "Trihalomethanes": 50.00, "Turbidity": 1.50,
    },
    "unsafe": {
        "ph": 3.85, "Hardness": 285.00, "Solids": 45200.00,
        "Chloramines": 11.40, "Sulfate": 445.00, "Conductivity": 640.00,
        "Organic_carbon": 22.80, "Trihalomethanes": 105.00, "Turbidity": 5.90,
    },
}

# -----------------------------------------------------------------------------
# 3. Sidebar
# -----------------------------------------------------------------------------
st.sidebar.title("💧 Water Quality Checker")
st.sidebar.markdown(
    "Checks whether water is **suitable for drinking (YES / NO)** "
    "from 9 physicochemical parameters."
)

st.sidebar.subheader("⚙️ Decision Threshold")
threshold = st.sidebar.slider(
    "Minimum share of parameters within safe limits",
    min_value=0.50, max_value=1.00, value=0.90, step=0.05,
    help="0.90 means all 9 parameters must pass. Lower values allow some to fail.",
)

st.sidebar.subheader("⚡ Quick Test Presets")
if "preset" not in st.session_state:
    st.session_state.preset = "median"

col_p1, col_p2 = st.sidebar.columns(2)
if col_p1.button("Dataset Median", use_container_width=True):
    st.session_state.preset = "median"
if col_p2.button("Clean Sample", use_container_width=True):
    st.session_state.preset = "clean"
if st.sidebar.button("Contaminated Sample", use_container_width=True):
    st.session_state.preset = "unsafe"

vals = presets[st.session_state.preset]

# -----------------------------------------------------------------------------
# 4. Input Form
# -----------------------------------------------------------------------------
st.title("🚰 Smart Water Quality Prediction System")
st.markdown(
    "Enter the measured water parameters below and click **Check Water Potability**."
)

with st.form("water_input_form"):
    c1, c2, c3 = st.columns(3)

    with c1:
        ph = st.number_input("pH Level (0 - 14)", 0.0, 14.0, float(vals["ph"]), 0.05,
                             help="Neutral = 7.0 (WHO guideline: 6.5 - 8.5).")
        chloramines = st.number_input("Chloramines (ppm)", 0.0, 15.0, float(vals["Chloramines"]), 0.1)
        organic_carbon = st.number_input("Organic Carbon (ppm)", 0.0, 35.0, float(vals["Organic_carbon"]), 0.1)

    with c2:
        hardness = st.number_input("Hardness (mg/L)", 0.0, 400.0, float(vals["Hardness"]), 1.0)
        sulfate = st.number_input("Sulfate (mg/L)", 0.0, 600.0, float(vals["Sulfate"]), 1.0)
        trihalomethanes = st.number_input("Trihalomethanes (μg/L)", 0.0, 150.0, float(vals["Trihalomethanes"]), 0.5)

    with c3:
        solids = st.number_input("Total Dissolved Solids (ppm)", 0.0, 70000.0, float(vals["Solids"]), 100.0)
        conductivity = st.number_input("Conductivity (μS/cm)", 0.0, 900.0, float(vals["Conductivity"]), 5.0)
        turbidity = st.number_input("Turbidity (NTU)", 0.0, 10.0, float(vals["Turbidity"]), 0.05)

    submitted = st.form_submit_button("🔍 Check Water Potability", type="primary", use_container_width=True)

# -----------------------------------------------------------------------------
# 5. Result
# -----------------------------------------------------------------------------
if submitted:
    inputs = {
        "ph": ph, "Hardness": hardness, "Solids": solids,
        "Chloramines": chloramines, "Sulfate": sulfate,
        "Conductivity": conductivity, "Organic_carbon": organic_carbon,
        "Trihalomethanes": trihalomethanes, "Turbidity": turbidity,
    }

    rows = []
    for key, value in inputs.items():
        label, lo, hi = LIMITS[key]
        ok = lo <= value <= hi
        rows.append({
            "Parameter": label,
            "Your Input": value,
            "Safe Range": f"{lo:g} - {hi:g}",
            "Status": "✅ Pass" if ok else "❌ Fail",
        })
    result_df = pd.DataFrame(rows)

    passed = int((result_df["Status"] == "✅ Pass").sum())
    total = len(result_df)
    score = passed / total
    is_potable = score >= threshold

    st.markdown("---")
    st.subheader("📋 Prediction Result")
    res_col1, res_col2 = st.columns([2, 1])

    with res_col1:
        if is_potable:
            st.markdown(
                f"""
                <div class="result-yes">
                    <div class="big-verdict">✅ YES — Suitable for Drinking</div>
                    <p style="font-size:16px; margin:0;">
                        <strong>{passed} of {total}</strong> parameters are within safe limits
                        (required: {threshold:.0%}).
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(
                f"""
                <div class="result-no">
                    <div class="big-verdict">❌ NO — Not Suitable for Drinking</div>
                    <p style="font-size:16px; margin:0;">
                        Only <strong>{passed} of {total}</strong> parameters are within safe limits
                        (required: {threshold:.0%}).
                    </p>
                </div>
                """, unsafe_allow_html=True)

    with res_col2:
        st.metric("Parameters within limits", f"{passed} / {total}")
        st.progress(score)
        st.caption(f"Decision Rule: YES if share passing ≥ {threshold:.0%}")

    st.subheader("🔬 Parameter Check")
    st.dataframe(
        result_df.style.format({"Your Input": "{:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "Limits are based on general WHO/EPA drinking-water guidance. "
        "This is a screening tool, not a substitute for laboratory testing."
    )