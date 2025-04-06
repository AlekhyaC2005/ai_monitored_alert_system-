import streamlit as st
import requests
import time
import os
import praw
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pywhatkit as kit

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
            font-size: 18px;
        }
        h1, h2, h3 {
            font-size: 36px !important;
        }
        .stButton > button {
            color: white !important;
            background-color: #1f77b4 !important;
            border-radius: 8px !important;
        }
        .stButton > button:hover {
            background-color: #105A8A !important;
        }
        .stTextArea textarea {
            font-size: 20px !important;
        }
        .stRadio label {
            font-size: 22px !important;
        }
        .stTextInput input {
            font-size: 20px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to", ["Home", "Feedback", "Admin Dashboard"])

# --- Home Page ---
if page == "Home":
    st.image("back_image.jpg")
    st.title("⚠ AI-Powered Multichannel Sentiment Monitoring & Real-Time Issue Detection for Events")
    st.markdown("""
    ### Problem:
    Event organizers often struggle to track attendee sentiment in real time, relying on delayed surveys and manual monitoring of social media and feedback channels. Negative experiences—such as long queues, poor audio quality, overcrowding, or dissatisfaction with speakers—often go unnoticed until after the event, leading to missed opportunities for immediate intervention.

    ### Our Solution:
    We’ve built an AI-powered real-time sentiment monitoring and issue detection system tailored for event organizers and product teams.

    Key features include:
    - Live Sentiment Analysis: Instantly classifies user feedback into Positive, Neutral, or Negative using NLP models.
    - Critical Issue Detection: Identifies keywords indicating problems like crashes, lag, bugs, or poor usability.
    - Instant Notifications: Triggers WhatsApp alerts to notify admins of critical user issues in real time.
    - Integrated Feedback & QnA Module: Collects both subjective and structured feedback through forms.
    - Scalable Architecture: Lightweight, modular design using FastAPI and Streamlit for future integrations.
    """)

# --- Feedback Page ---
elif page == "Feedback":
    st.image("home.jpg", width=300)
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

elif page == "Admin Dashboard":
    st.image("d.jpg")
    st.subheader("🛠️ Admin Dashboard")

    topic = st.text_input("Enter a topic to analyze posts:")

    if st.button("Fetch Comments & Analyze"):
        with st.spinner("Fetching comments..."):
            # Fetch all comments for a topic using Reddit API
            reddit = praw.Reddit(
                client_id="0GsblhgdFh2tJHxs4QLC_Q",
                client_secret="D9QFWl-JJwS-7ii_1U5Gljv4EDxjrQ",
                user_agent="Disastrous-Back-6404"
            )
            analyzer = SentimentIntensityAnalyzer()
            comments_data = []
            try:
                for submission in reddit.subreddit("all").search(topic, limit=20):
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list()[:5]:
                        text = comment.body
                        score = analyzer.polarity_scores(text)['compound']
                        label = "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
                        comments_data.append({"text": text, "sentiment": label})



                df = pd.DataFrame(comments_data)
                if df.empty:
                    st.warning("No comments found for the given topic.")
                else:
                    st.success(f"Fetched {len(df)} comments!")
                    st.dataframe(df)

                    # Plot Sentiment Distribution
                    sentiment_counts = df["sentiment"].value_counts()
                    st.subheader("📊 Sentiment Distribution")

                    col1, col2 = st.columns(2)
                    with col1:
                        fig1, ax1 = plt.subplots()
                        ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%',
                                colors=['green', 'gray', 'red'], startangle=90)
                        ax1.set_title("Sentiment Breakdown")
                        st.pyplot(fig1)

                    with col2:
                        fig2, ax2 = plt.subplots()
                        sns.barplot(x=sentiment_counts.index, y=sentiment_counts.values,
                                    palette=["green", "gray", "red"], ax=ax2)
                        ax2.set_title("Sentiment Counts")
                        st.pyplot(fig2)

                    # Word Cloud for Negative Comments
                    st.subheader("⚠️ Common Words in Negative Comments")
                    negative_comments = " ".join(df[df["sentiment"] == "Negative"]["text"].tolist())
                    if negative_comments:
                        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(negative_comments)
                        fig3, ax3 = plt.subplots()
                        ax3.imshow(wordcloud, interpolation="bilinear")
                        ax3.axis("off")
                        st.pyplot(fig3)

                    # Sentiment Trend Over Time
                    df["sentiment_score"] = df["sentiment"].map({"Positive": 1, "Neutral": 0, "Negative": -1})
                    df["cumulative_sentiment"] = df["sentiment_score"].cumsum()
                    st.subheader("📈 Sentiment Trend Over Time")
                    fig4, ax4 = plt.subplots()
                    sns.lineplot(data=df, x=df.index, y="cumulative_sentiment", marker="o", ax=ax4)
                    st.pyplot(fig4)

                    # Filter and Analyze Complaints
                    st.subheader("🔥 Most Common Complaints")
                    ISSUE_KEYWORDS = [
                        "bad", "worst", "awful", "terrible", "poor", "horrible", "disappointing", "broken",
                        "frustrating", "slow", "lag", "crash", "bug", "glitch", "fail", "not working",
                        "hate", "waste", "useless", "unreliable", "pathetic", "error", "stuck", "freeze", "hang"
                    ]
                    complaint_df = df[df["text"].str.lower().apply(lambda x: any(kw in x for kw in ISSUE_KEYWORDS))]
                    if complaint_df.empty:
                        st.warning("No common complaints found from the keyword list.")
                    else:
                        from collections import Counter

                        def count_keywords(text):
                            return [kw for kw in ISSUE_KEYWORDS if kw in text]

                        keywords_found = []
                        for row in complaint_df["text"].str.lower():
                            keywords_found.extend(count_keywords(row))

                        keyword_counts = Counter(keywords_found).most_common(15)
                        keyword_df = pd.DataFrame(keyword_counts, columns=["Keyword", "Frequency"])
                        st.dataframe(keyword_df)

                        fig_k, ax_k = plt.subplots()
                        sns.barplot(data=keyword_df, x="Frequency", y="Keyword", palette="Reds_r", ax=ax_k)
                        ax_k.set_title("Top Complaint Keywords")
                        st.pyplot(fig_k)

                        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(dict(keyword_counts))
                        fig_wc, ax_wc = plt.subplots()
                        ax_wc.imshow(wordcloud, interpolation="bilinear")
                        ax_wc.axis("off")
                        st.subheader("☁️ Word Cloud of Frequent Complaints")
                        st.pyplot(fig_wc)
            except Exception as e:
                st.error(f"Error fetching comments: {e}")
