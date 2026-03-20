import streamlit as st
import pandas as pd
import cv2
import tempfile
import time
import datetime
import os

# Set Page Config
st.set_page_config(page_title="Indian Railways Loco Crew Monitoring", layout="wide")

def mock_ai_analysis(video_path):
    """
    PLACEHOLDER FOR YOUR ACTUAL AI MODEL.
    This simulates frame-by-frame analysis every 2 seconds.
    The dummy data below reflects the image provided by the user.
    """
    # Simulating processing delay
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.02)
        progress_bar.progress(i + 1)
        
    # Mock extracted data based on the provided frame
    report_data = {
        "Loco_ID": "WAG-9 31XXX", # Dummy ID
        "Date": "08-03-2025",
        "Start_Time": "12:26:38",
        "End_Time": "12:28:38",
        "Condition": "Running",
        "Analysis_Text": (
            "During the observation period, the locomotive was detected to be in a RUNNING condition. "
            "Both LP and ALP are in the correct uniform (Sky Blue Shirt). "
            "The Loco Pilot (LP) is standing at the Driving Desk and appears alert. "
            "However, the Assistant Loco Pilot (ALP) is observed sitting and performing writing work in the logbook while the train is in motion, "
            "which is a violation of operating manuals."
        ),
        "Compliance_Table":[
            {
                "Timestamp (Video Clock)": "12:26:38",
                "Timestamp (Video Streaming)": "00:00:00",
                "Activity Category": "Writing Work",
                "Compliance Status": "Non-Compliant",
                "Deviation Description": "ALP is performing writing work while the locomotive is in running condition."
            },
            {
                "Timestamp (Video Clock)": "12:26:45",
                "Timestamp (Video Streaming)": "00:00:07",
                "Activity Category": "Alertness",
                "Compliance Status": "Compliant",
                "Deviation Description": "LP is alert and monitoring the track ahead from the Driving Desk."
            }
        ],
        "Disciplinary": {
            "Corrective Measures": "Counseling of ALP at the crew lobby regarding the prohibition of writing work (filling logbooks/diaries) while the locomotive is in motion. Refresher on distraction rules.",
            "Charge Sheet & Punishment": "Minor Penalty (SF-11) for ALP under DAR norms for negligence of safety protocols during running condition."
        }
    }
    return report_data

def main():
    st.title("🚆 Indian Railway Locomotive Crew Monitoring Analysis")
    st.markdown("""
    **Role:** Expert Video Analyst  
    **Framework:** Indian Railway Codes, G&SR, Accident Manuals  
    **Scope:** Conventional & 3-Phase Locomotives (Frame-by-Frame Analysis every 2 seconds)
    """)
    
    st.divider()

    # Layout: Two columns. Left for Video Upload, Right for Feedback.
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Upload Loco Cab Video")
        st.info("Maximum allowed size: 300 MB. Supported formats: MP4, AVI, MOV.")
        
        uploaded_video = st.file_uploader("Upload Video File", type=['mp4', 'avi', 'mov'])
        
        if uploaded_video is not None:
            # Save uploaded video to a temporary file for OpenCV processing
            tfile = tempfile.NamedTemporaryFile(delete=False) 
            tfile.write(uploaded_video.read())
            
            st.video(uploaded_video)
            
            if st.button("▶️ Run AI Frame-by-Frame Analysis", type="primary"):
                with st.spinner("Analyzing frames every 2 seconds using vision models..."):
                    report = mock_ai_analysis(tfile.name)
                    st.session_state['report'] = report
                st.success("Analysis Complete!")

    with col2:
        st.subheader("🛠️ AI Feedback & Retraining Loop")
        st.markdown("If the physical inspection differs from the AI detection, feed the corrected data here to improve the model.")
        
        with st.form("feedback_form", clear_on_submit=True):
            f_time = st.text_input("Timestamp (e.g., 12:26:38)")
            f_role = st.selectbox("Crew Member",["LP", "ALP", "Both"])
            f_actual = st.selectbox("Actual Physical Activity",[
                "Signal Calling", "Alert/Looking Ahead", "Nap/Micro-Sleep", 
                "Distraction", "Mobile Usage", "Writing Work", 
                "RS Valve Hand placement", "Exchange Signals", "Horn Operation",
                "Packing", "Leaving Seat", "Loco Check (Stationary)", 
                "SA-9 Application", "Reverser Neutral"
            ])
            f_comments = st.text_area("Detailed Comments for Model Correction")
            
            submitted = st.form_submit_button("Submit Correction Data")
            if submitted:
                # In a real app, save this to a database (PostgreSQL, MongoDB) or CSV
                # For example: pd.DataFrame([[f_time, f_role, f_actual, f_comments]]).to_csv('feedback.csv', mode='a')
                st.success("Feedback logged! This data will be used for the next AI model retraining cycle.")

    st.divider()

    # Display Report if available in session state
    if 'report' in st.session_state:
        report = st.session_state['report']
        
        st.header("📄 Locomotive Crew Monitoring Analysis Report")
        
        # Subheadings
        st.markdown(f"**Locomotive ID:** `{report['Loco_ID']}`")
        st.markdown(f"**Date of Recording:** `{report['Date']}`")
        st.markdown(f"**Observation Period:** `{report['Start_Time']}` to `{report['End_Time']}`")
        
        st.subheader("Detailed Analysis")
        st.write(report['Analysis_Text'])
        
        st.subheader("Compliance Summary & Deviation Table")
        df_compliance = pd.DataFrame(report['Compliance_Table'])
        
        # Styling the dataframe to highlight Non-Compliant rows
        def highlight_non_compliant(row):
            if row['Compliance Status'] == 'Non-Compliant':
                return['background-color: #ffcccc; color: #900000'] * len(row)
            return [''] * len(row)
            
        styled_df = df_compliance.style.apply(highlight_non_compliant, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        st.subheader("Disciplinary Summary")
        st.error(f"**Corrective Measures:**\n{report['Disciplinary']['Corrective Measures']}")
        st.warning(f"**Charge Sheet & Punishment:**\n{report['Disciplinary']['Charge Sheet & Punishment']}")

if __name__ == '__main__':
    main()
