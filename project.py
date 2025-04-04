import streamlit as st
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pywhatkit as kit
import os
import time

# WhatsApp Notification Setup
PHONE_NUMBER = "+919831513919"
os.environ["DISPLAY"] = ":99.0"

# Keywords to detect issues
ISSUE_KEYWORDS = [
    "bad", "worst", "awful", "terrible", "poor", "horrible", "disappointing", "broken", 
    "frustrating", "slow", "lag", "crash", "bug", "glitch", "fail", "not working", 
    "hate", "waste", "useless", "unreliable", "pathetic"
]

def check_issues_and_notify(text):
    detected = [w for w in ISSUE_KEYWORDS if w in text.lower()]
    if detected:
        msg = f"🚨 Issue Detected: {', '.join(detected)}\nFeedback: {text}"
        try:
            kit.sendwhatmsg_instantly(PHONE_NUMBER, msg, wait_time=10, tab_close=True)
        except Exception as e:
            print("WhatsApp error:", e)

# Set background color and button styles
st.markdown("""
    <style>
        body {
            background-color: #e6f7ff;
        }
        .stButton > button {
            color: white !important;
            background-color: #1f77b4 !important;
            border-radius: 8px !important;
        }
        .stButton > button:hover {
            background-color: #105A8A !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to", ["Home", "Feedback", "Admin Dashboard"])

if page == "Home":
    st.title("⚠ AI-Powered Multichannel Sentiment Monitoring & Real-Time Issue Detection for Events")
    st.markdown("""
    ### Problem:
    Event organizers often struggle to track attendee sentiment in real time, relying on delayed surveys and manual monitoring of social media and feedback channels.

    ### Our Solution:
    This platform uses AI-powered sentiment analysis to monitor feedback and social media discussions in real-time. It automatically:
    - Analyzes sentiments (Positive, Neutral, Negative)
    - Detects issue-related keywords
    - Sends instant WhatsApp alerts when critical issues are mentioned
    """)

elif page == "Feedback":
    st.title("📝 Submit Your Feedback")

    feedback_text = st.text_area("Tell us about your experience with the product:")
    if st.button("Submit Feedback"):
        if feedback_text.strip():
            with st.spinner("Analyzing sentiment..."):
                response = requests.post("http://127.0.0.1:8000/analyze", json={"text": feedback_text})
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Sentiment: {result['sentiment']}")
                else:
                    st.error("Error analyzing sentiment.")
        else:
            st.warning("Please enter some feedback before submitting.")

    st.markdown("---")
    st.subheader("📋 Product Q&A Form")

    q1 = st.radio("1. How would you rate the product quality?", ["Excellent", "Good", "Average", "Poor"])
    q2 = st.radio("2. Was the product easy to use?", ["Yes", "Somewhat", "No"])
    q3 = st.radio("3. Did the product meet your expectations?", ["Yes", "No"])
    q4 = st.radio("4. Would you recommend this product to others?", ["Definitely", "Maybe", "No"])
    q5 = st.text_area("5. Any specific issue you faced?")

    if st.button("Submit Q&A"):
        with st.spinner("Submitting your responses..."):
            time.sleep(2)
            if q5.strip():
                check_issues_and_notify(q5)
            st.success("Your response has been recorded!")

elif page == "Admin Dashboard":
    st.title("📊 Analytics (Coming Soon)")
    st.info("This section will visualize collected feedback and sentiment trends.")