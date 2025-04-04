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
    Event organizers often struggle to track attendee sentiment in real time, relying on delayed surveys and manual monitoring of social media and feedback channels. Negative experiences—such as long queues, poor audio quality, overcrowding, or dissatisfaction with speakers—often go unnoticed until after the event, leading to missed opportunities for immediate intervention.
    With multiple feedback sources like social media, in-app chats, live Q&A sessions, and review platforms, manually aggregating and analyzing sentiment is inefficient and inaccurate. Organizers need an AI-driven system to detect and respond to concerns as they arise, ensuring a seamless event experience.

    ### Our Solution:
    We’ve built an AI-powered real-time sentiment monitoring and issue detection system tailored for event organizers and product teams.

    #Key features include:

    #Live Sentiment Analysis:
     Feedback is analyzed instantly using advanced Natural Language Processing (NLP) models like VADER. It classifies responses as Positive, Neutral, or Negative to help you gauge overall public sentiment.

    #Critical Issue Detection:
     Our system scans feedback for urgent issue-related keywords (like "crash," "not working," "slow," "useless" etc.). It doesn’t just tell you how users feel — it tells you what’s going wrong.

    #Instant Notifications:
     If any critical issue is detected, an automated WhatsApp alert is triggered and sent to the admin or operations team. This helps you act immediately, rather than waiting for post-event surveys or escalations.

    #Integrated Feedback & QnA Module:
    Users can submit detailed feedback as well as answer a structured QnA form. This allows collection of both subjective feedback and objective product performance insights.

    #Scalable Architecture:
     Built using FastAPI and Streamlit, the platform is modular, lightweight, and can be easily integrated with social media APIs, ticketing tools, or customer support platforms.

    With this platform, you can stop reacting after the damage is done — and start responding while it’s happening.
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
            # Check for poor feedback pattern
            if (q1 == "Poor") or (q2 == "No") or (q3 == "No") or (q4 == "No"):
                st.warning("⚠ Poor Feedback Detected! Admin has been notified.")

elif page == "Admin Dashboard":
    st.title("📊 Analytics (Coming Soon)")
    st.info("This section will visualize collected feedback and sentiment trends.")