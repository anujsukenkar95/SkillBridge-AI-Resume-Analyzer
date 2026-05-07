import streamlit as st
import pandas as pd
import logic
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(page_title="SkillBridge AI", page_icon="🚀", layout="wide")

# --- CUSTOM CSS (Footer & Styling) ---
st.markdown("""
<style>
    /* Remove top margin */
    .main > div {padding-top: 2rem;}
    
    /* Hide sidebar scrollbar for a clean, fixed app look */
    [data-testid="stSidebar"] div::-webkit-scrollbar {
        display: none;
    }
    [data-testid="stSidebar"] {
        -ms-overflow-style: none;  /* IE and Edge */
        scrollbar-width: none;  /* Firefox */
    }
    
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
    # Create two columns: a small one for the logo, a wider one for the text
    col_logo, col_text = st.columns([1, 4])
    
    with col_logo:
        st.image("https://cdn-icons-png.flaticon.com/512/3096/3096677.png", width=60)
        
    with col_text:
        # Using HTML to remove the default gaps and make it look perfectly aligned
        st.markdown("<h2 style='margin-top: -15px; margin-bottom: 0px;'>SkillBridge</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px; color: #808080; margin-top: -10px;'>AI-Powered Resume Analyser</p>", unsafe_allow_html=True)
        
    st.divider()
    
    uploaded_files = st.file_uploader("1. Upload Resumes (Batch PDF)", type="pdf", accept_multiple_files=True)

    job_desc = st.text_area("2. Paste Job Description", height=200, placeholder="Paste JD here...")
    
    analyze_btn = st.button("Analyze Profile", type="primary", use_container_width=True)
    
    st.divider()
    st.info("💡 Tip: Ensure the resume is text-based.")

# --- MAIN CONTENT ---
st.subheader(" Candidate Analysis Dashboard")

# --- INITIALIZE MEMORY (SESSION STATE) ---
# This ensures the app doesn't forget our data when we click the dropdown
if 'batch_results' not in st.session_state:
    st.session_state['batch_results'] = None

# --- PROCESS THE BUTTON CLICK ---
if analyze_btn:
    if uploaded_files and job_desc:
        with st.spinner(f"Processing {len(uploaded_files)} resumes..."):
            results = []
            
            for file in uploaded_files:
                resume_text = logic.extract_text_from_pdf(file)
                
                if resume_text:
                    # Calculate Score
                    score, missing = logic.calculate_match(resume_text, job_desc, nlp)
                    
                    # Extract Personal Info
                    info = logic.extract_personal_info(resume_text, nlp)
                    
                    # Save EVERYTHING to our results list
                    results.append({
                        "File Name": file.name,
                        "Candidate Name": info["Name"] if info["Name"] != "Not Found" else file.name.replace(".pdf", ""),
                        "Email": info["Email"],
                        "Phone": info["Phone"],
                        "Match Score (%)": score,
                        "Missing Skills": ", ".join(missing).title() if missing else "None (Perfect Match)",
                        "Raw Text": resume_text # Saving this so we can read it later
                    })
                else:
                    st.error(f"❌ Failed to read {file.name}")
            
            # Save the final results into Streamlit's memory
            st.session_state['batch_results'] = results
    else:
        st.warning("⚠️ Please upload at least one resume and paste the JD.")

# --- DISPLAY THE DASHBOARD (Reads from Memory) ---
# Because this is outside the button click, the dropdown will now work perfectly!
if st.session_state['batch_results']:
    st.divider()
    st.subheader("🏆 ATS Leaderboard & Rankings")
    
    # Create the DataFrame
    df = pd.DataFrame(st.session_state['batch_results'])
    df = df.sort_values(by="Match Score (%)", ascending=False).reset_index(drop=True)
    df.index = df.index + 1 
    
    # Show the table (Hiding the raw text and email/phone from the main view to keep it clean)
    display_df = df[["Candidate Name", "Match Score (%)", "Missing Skills"]]
    st.dataframe(
        display_df.style.highlight_max(subset=['Match Score (%)'], color='#2E86C1'),
        use_container_width=True
    )
    
    # --- DETAILED CANDIDATE BREAKDOWN ---
    st.divider()
    st.subheader("📊 Detailed Candidate Breakdown")
    
    # The dropdown will now work without erasing the page!
    selected_candidate = st.selectbox(
        "Select or search for a candidate to view full profile:", 
        options=df["Candidate Name"],
        index=None, 
        placeholder="🔍 Type candidate name to search..."
    )
    
    # We must add an 'if' statement so it doesn't try to load data before you select someone!
    if selected_candidate:
        # Get the specific data for the selected candidate
        candidate_data = df[df["Candidate Name"] == selected_candidate].iloc[0]
    
        # Display the Extracted Profile (Option A integrated!)
        st.markdown("### 👤 Candidate Profile")
        col1, col2, col3 = st.columns(3)
        col1.info(f"**Name:**\n{candidate_data['Candidate Name']}")
        col2.success(f"**Email:**\n{candidate_data['Email']}")
        col3.warning(f"**Phone:**\n{candidate_data['Phone']}")
        
        # Display Score and Gaps
        st.markdown("### ⚠️ Gap Analysis")
        st.write(f"**Match Score:** {candidate_data['Match Score (%)']}%")
        if candidate_data['Missing Skills'] != "None (Perfect Match)":
            st.error(f"**Missing Skills:** {candidate_data['Missing Skills']}")
        else:
            st.success("No missing skills found!")
            
        # Display the Raw Extracted Data
        with st.expander("📄 View Extracted Resume Text"):
            st.text(candidate_data['Raw Text'])

elif not analyze_btn:
    st.info("🛞 Waiting for input... Upload resumes and click Analyze.")

# --- 2. COPYRIGHT FOOTER (Fixed at Bottom) ---
st.markdown("""
<div class="footer">

                SkillBridge AI © 2025 | Developed by SkillBridge Team | BCA Final Year Project
</div>
""", unsafe_allow_html=True)