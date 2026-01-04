import streamlit as st
import logic
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(page_title="SkillBridge AI", page_icon="🚀", layout="wide")

# --- CUSTOM CSS (Footer & Styling) ---
st.markdown("""
<style>
    /* Remove top margin */
    .main > div {padding-top: 2rem;}
    
    /* Footer Styling */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0E1117;
        color: #808080;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        border-top: 1px solid #262730;
        z-index: 100;
    }
</style>
""", unsafe_allow_html=True)

# --- CACHING THE BRAIN ---
@st.cache_resource
def get_model():
    return logic.load_nlp_model()

with st.spinner("Waking up AI Brain..."):
    nlp = get_model()

# --- SIDEBAR ---
with st.sidebar:
    # 1. FIXED LOGO SIZE (Smaller: width=50)
    st.image("https://cdn-icons-png.flaticon.com/512/3096/3096677.png", width=50)
    
    st.title("SkillBridge")
    st.caption("AI-Powered Resume Analysis")
    st.divider()
    
    uploaded_file = st.file_uploader("1. Upload Resume (PDF)", type="pdf")
    job_desc = st.text_area("2. Paste Job Description", height=200, placeholder="Paste JD here...")
    
    analyze_btn = st.button("Analyze Profile 🚀", type="primary", use_container_width=True)
    
    st.divider()
    st.info("💡 Tip: Ensure the resume is text-based.")

# --- MAIN CONTENT ---
st.subheader("📊 Candidate Analysis Dashboard")

if analyze_btn:
    if uploaded_file and job_desc:
        resume_text = logic.extract_text_from_pdf(uploaded_file)
        
        if not resume_text:
            st.error("❌ Failed to read PDF. Please try a different file.")
        else:
            # --- CALCULATION ---
            score, missing = logic.calculate_match(resume_text, job_desc, nlp)
            
            # --- ROW 1: SCORE GAUGE ---
            col1, col2 = st.columns([1, 2])
            
            with col1:
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = score,
                    title = {'text': "Relevance Score"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#2E86C1"},
                        'steps': [
                            {'range': [0, 50], 'color': "#FFCDD2"},
                            {'range': [50, 75], 'color': "#FFF9C4"},
                            {'range': [75, 100], 'color': "#C8E6C9"}
                        ],
                    }
                ))
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # --- CATEGORIZED FEEDBACK ---
                st.markdown("### ⚠️ Skill Gap Analysis")
                if not missing:
                    st.success("🎉 Incredible! You are a perfect match for this job.")
                    st.balloons()
                else:
                    st.write("We found the following gaps in your profile:")
                    
                    tab1, tab2, tab3 = st.tabs(["Technical Gaps", "Soft Skills", "All Missing"])
                    
                    with tab1:
                        # Tech Categories
                        tech_cats = ["Languages", "Frameworks & Libs", "Tools & Cloud"]
                        found_tech_gap = False
                        for cat in tech_cats:
                            if cat in logic.SKILL_DB: # Safety check
                                cat_missing = [s for s in missing if s in logic.SKILL_DB[cat]]
                                if cat_missing:
                                    found_tech_gap = True
                                    st.error(f"**{cat}:** {', '.join(cat_missing).upper()}")
                        
                        if not found_tech_gap:
                            st.info("✅ No technical skill gaps found!")

                    with tab2:
                        # Soft Skills
                        soft_missing = [s for s in missing if s in logic.SKILL_DB["Soft Skills"]]
                        if soft_missing:
                            st.warning(f"Consider adding: {', '.join(soft_missing).title()}")
                        else:
                            st.info("✅ Soft skills look good.")
                            
                    with tab3:
                        st.write(f"Total Missing Keywords: {len(missing)}")
                        st.markdown(f"`{', '.join(missing)}`")

            # --- RESUME PREVIEW ---
            with st.expander("📄 View Extracted Resume Data"):
                st.text(resume_text)

    else:
        st.warning("⚠️ Please complete steps 1 and 2 in the sidebar.")
else:
    st.info("👈 Waiting for input... Upload a resume to start.")

# --- 2. COPYRIGHT FOOTER (Fixed at Bottom) ---
st.markdown("""
<div class="footer">

    SkillBridge AI © 2025 | Developed by [Your Name] | BCA Final Year Project
</div>
""", unsafe_allow_html=True)