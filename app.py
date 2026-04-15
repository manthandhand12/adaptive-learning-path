import streamlit as st
import pandas as pd

# This line helps Vercel's build process pass
app = st.write 

st.set_page_config(page_title="Adaptive Learning Path", layout="wide")

st.title("🎓 Adaptive Learning Path")
st.write("Welcome to your student analytics dashboard.")

# Sidebar for inputs
st.sidebar.header("Student Data")
attendance = st.sidebar.slider("Attendance %", 0, 100, 80)
study_hours = st.sidebar.slider("Weekly Study Hours", 0, 50, 20)

# Display a result
st.subheader("Performance Analysis")
if attendance < 75:
    st.warning("⚠️ Student is at risk due to low attendance.")
else:
    st.success("✅ Student performance is stable.")
