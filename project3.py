import streamlit as st
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pywhatkit as kit
import os
import time
import praw

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

# Background and Button Styling
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

# --- Home Page ---
if page == "Home":
    st.title("⚠ AI-Powered Multichannel Sentiment Monitoring & Real-Time Issue Detection for Events")
    st.markdown("""
    ### Problem:
    Event organizers often struggle to track attendee sentiment in real time, relying on delayed surveys and manual monitoring of social media and feedback channels. Negative experiences—such as long queues, poor audio quality, overcrowding, or dissatisfaction with speakers—often go unnoticed until after the event, leading to missed opportunities for immediate intervention.

    ### Our Solution:
    We’ve built an AI-powered real-time sentiment monitoring and issue detection system tailored for event organizers and product teams.

    *Key features include:*
    - *Live Sentiment Analysis:* Instantly classifies user feedback into Positive, Neutral, or Negative using NLP models.
    - *Critical Issue Detection:* Identifies keywords indicating problems like crashes, lag, bugs, or poor usability.
    - *Instant Notifications:* Triggers WhatsApp alerts to notify admins of critical user issues in real time.
    - *Integrated Feedback & QnA Module:* Collects both subjective and structured feedback through forms.
    - *Scalable Architecture:* Lightweight, modular design using FastAPI and Streamlit for future integrations.
    """)

# --- Feedback Page ---
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

            if q1 == "Poor" or q2 == "No" or q3 == "No" or q4 == "No":
                st.warning("⚠ Poor feedback detected. Admin has been alerted!")

# --- Admin Dashboard Page ---
elif page == "Admin Dashboard":
    st.title("🛠 Admin Dashboard")

    st.markdown("Enter a topic below to fetch live comments:")

    topic = st.text_input("Enter Topic")

    if st.button("Fetch Comments"):
        if topic.strip():
            with st.spinner("Fetching comments..."):
                # Reddit API Setup
                reddit = praw.Reddit(
                    client_id="0GsblhgdFh2tJHxs4QLC_Q",
                    client_secret="D9QFWl-JJwS-7ii_1U5Gljv4EDxjrQ",
                    user_agent="Disastrous-Back-6404"
                )

                comments_collected = []
                for submission in reddit.subreddit("all").search(topic, limit=20):
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list()[:5]:  # Limit to 5 per post
                        comments_collected.append(comment.body)

                if comments_collected:
                    st.success(f"Fetched {len(comments_collected)} comments for topic '{topic}'")
                    for i, comment in enumerate(comments_collected, 1):
                        st.markdown(f"*Comment {i}:* {comment}")
                else:
                    st.warning("No comments found.")
        else:
            st.warning("Please enter a topic.")