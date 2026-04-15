import streamlit as st
import pandas as pd

# Required for Vercel
app = st.write 

st.set_page_config(page_title="Adaptive Learning Path", layout="wide")

st.title("🎓 Adaptive Learning Path")
st.write("Analyze student risk levels based on multiple performance metrics.")

# Sidebar for inputs
st.sidebar.header("Student Metrics")
attendance = st.sidebar.slider("Attendance %", 0, 100, 80)
study_hours = st.sidebar.slider("Weekly Study Hours", 0, 50, 20)
marks = st.sidebar.number_input("Current Marks (out of 100)", 0, 100, 70)

# Performance Logic
# We create a weighted score (Marks 50%, Attendance 30%, Study Hours 20%)
# Study hours are normalized (20+ hours = 100% score for that category)
study_score = min((study_hours / 20) * 100, 100)
final_score = (marks * 0.5) + (attendance * 0.3) + (study_score * 0.2)

st.markdown("---")
st.subheader("Performance Analysis")

col1, col2 = st.columns(2)

with col1:
    st.metric(label="Overall Performance Score", value=f"{round(final_score, 1)}%")

with col2:
    if final_score < 50:
        st.error("🔴 Status: High Risk")
        st.info("Recommendation: Immediate intervention and extra tutoring required.")
    elif 50 <= final_score < 75:
        st.warning("🟡 Status: Moderate Risk")
        st.info("Recommendation: Increase study hours and monitor upcoming tests.")
    else:
        st.success("🟢 Status: Low Risk / Excelling")
        st.info("Recommendation: Continue current path. Suggest advanced modules.")

# Detailed Breakdown
with st.expander("See Detailed Breakdown"):
    st.write(f"- **Academic Impact (Marks):** {'Good' if marks > 60 else 'Needs Improvement'}")
    st.write(f"- **Engagement (Attendance):** {'High' if attendance > 75 else 'Low'}")
    st.write(f"- **Effort (Study Hours):** {'Sufficient' if study_hours >= 15 else 'Insufficient'}")
