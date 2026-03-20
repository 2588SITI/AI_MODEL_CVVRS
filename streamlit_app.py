import streamlit as st
import cv2
import tempfile
import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# ------------------------------
# Utility Functions
# ------------------------------

def detect_motion(frame1, frame2):
    """Detect motion between two frames to decide if train is running."""
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 25, 255, cv2.THRESH_BINARY)
    motion = np.sum(thresh) / 255
    return motion > 5000  # Threshold tuned for vibration/motion detection

def analyze_frame(frame, timestamp, motion_detected):
    """
    Analyze each frame for the activities and compliance status.
    This is a mock — in deployment, connect to your trained CV model.
    """
    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Placeholder detections (replace with AI detections)
    activity_category = "Running Condition" if motion_detected else "Stationary Condition"
    compliance = "Compliant"
    deviation_desc = ""
    
    # Example rule-based detections (can be replaced with ML/YOLO+Pose model)
    # Detect writing: look for pen/book patterns
    avg_color = np.mean(rgb, axis=(0,1))
    if motion_detected:
        # Simulate that sometimes LP does writing work while train is moving
        if np.random.rand() < 0.15:
            compliance = "Non-Compliant"
            deviation_desc = "Writing while train is running"
    
    # Add more rule-based detections such as mobile, nap, distraction using your model later
    return {
        "Timestamp (Video Clock)": str(timestamp),
        "Timestamp (Video Streaming)": f"{timestamp.strftime('%H:%M:%S')}",
        "Activity Category": activity_category,
        "Compliance Status": compliance,
        "Deviation Description": deviation_desc
    }

def generate_report(df):
    non_compliant = df[df["Compliance Status"]=="Non-Compliant"]
    total_frames = len(df)
    total_non_compliant = len(non_compliant)
    compliance_rate = 100*(1 - total_non_compliant/total_frames)
    return f"""
    ## Locomotive Crew Monitoring Analysis Report

    **Locomotive ID:** Auto-detected or manual entry  
    **Date of Recording:** {datetime.now().strftime('%d-%m-%Y')}  
    **Observation Period:** As per video timestamp  

    ---
    ### Compliance Summary
    - Total Frames Analyzed: {total_frames}
    - Non-Compliant Frames: {total_non_compliant}
    - Compliance Rate: {compliance_rate:.2f}%

    ---
    ### Corrective Measures
    - Minor: Counseling for writing during running
    - Major: Disciplinary review if repeated across periods  

    """
# ------------------------------
# Streamlit UI
# ------------------------------

st.set_page_config(page_title="Indian Railway Locomotive Crew Monitoring", layout="wide")

st.title("🚆 Indian Railway Locomotive Crew Monitoring Analysis")

uploaded_video = st.file_uploader("Upload locomotive cab video (Max 300MB)", type=["mp4", "avi", "mov"])

if uploaded_video:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_video.read())
    st.video(tfile.name)

    start_btn = st.button("🚀 Run Video Analysis")

    if start_btn:
        cap = cv2.VideoCapture(tfile.name)
        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        interval = 2  # seconds
        df_data = []

        stframe = st.empty()
        prev_frame = None
        start_time = datetime(2025,3,8,12,26,38)  # Example extracted timestamp
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            if frame_pos % (frame_rate * interval) != 0:
                continue

            timestamp = start_time + timedelta(seconds=(frame_pos/frame_rate))
            if prev_frame is not None:
                motion = detect_motion(prev_frame, frame)
            else:
                motion = False

            record = analyze_frame(frame, timestamp, motion)
            df_data.append(record)
            prev_frame = frame
            stframe.image(frame, channels="BGR", caption=f"Analyzing frame at {timestamp.time()}")

        cap.release()
        df = pd.DataFrame(df_data)
        st.success("Analysis Completed ✅")

        st.write("### Compliance Summary & Deviation Table")
        st.dataframe(df)

        report_text = generate_report(df)
        st.markdown(report_text)

        # Download report
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Compliance Report (CSV)", csv, "compliance_report.csv", "text/csv")

        # Display corrective interface
        st.subheader("🧠 Feedback / Physical Inspection Correction")
        st.write("Use this form to correct AI detection misalignments so the model can learn.")

        with st.form("correction_form"):
            frame_time = st.text_input("Frame Timestamp (e.g., 12:26:38)")
            correct_activity = st.text_input("Correct Activity Category")
            correct_status = st.selectbox("Correct Compliance", ["Compliant", "Non-Compliant"])
            remarks = st.text_area("Remarks for future model improvement")
            submit_btn = st.form_submit_button("Submit Correction")

            if submit_btn:
                correction_data = {
                    "Frame_Timestamp": frame_time,
                    "Correct_Activity": correct_activity,
                    "Correct_Compliance": correct_status,
                    "Remarks": remarks,
                    "Recorded_At": str(datetime.now())
                }
                # Store corrections for retraining
                if not os.path.exists("corrections.csv"):
                    pd.DataFrame([correction_data]).to_csv("corrections.csv", index=False)
                else:
                    df_corr = pd.read_csv("corrections.csv")
                    df_corr = df_corr.append(correction_data, ignore_index=True)
                    df_corr.to_csv("corrections.csv", index=False)
                st.success("Correction saved successfully.")
