import streamlit as st
import requests
import pandas as pd
import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pywhatkit as kit

# WhatsApp Notification Settings
PHONE_NUMBER = "+919831513919"  # Ensure correct country code

# Keywords for issue detection
ISSUE_KEYWORDS = [
    "bad", "worst", "awful", "terrible", "poor", "horrible", "disappointing", "broken", 
    "frustrating", "slow", "lag", "crash", "bug", "glitch", "fail", "not working", 
    "hate", "waste", "useless", "unreliable", "pathetic"
]

# Reddit API authentication
reddit = praw.Reddit(
    client_id="0GsblhgdFh2tJHxs4QLC_Q",
    client_secret="D9QFWl-JJwS-7ii_1U5Gljv4EDxjrQ",
    user_agent="Disastrous-Back-6404"
)

# FastAPI Backend
app = FastAPI()
sentiment_analyzer = SentimentIntensityAnalyzer()

class Feedback(BaseModel):
    text: str

# Function to send WhatsApp message
def send_whatsapp_message(message):
    try:
        kit.sendwhatmsg_instantly(PHONE_NUMBER, message, wait_time=10)
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")

# Function to check for issue keywords and send WhatsApp alert
def check_issue_keywords_and_notify(feedback_text):
    detected_keywords = [word for word in ISSUE_KEYWORDS if word in feedback_text.lower()]
    
    if detected_keywords:
        keyword_list = ", ".join(detected_keywords)
        alert_message = f"🚨 Issue Alert: The following issue keyword(s) were detected: {keyword_list}\n\nFeedback: {feedback_text}"
        send_whatsapp_message(alert_message)

@app.post("/analyze")
def analyze_sentiment(feedback: Feedback):
    sentiment = sentiment_analyzer.polarity_scores(feedback.text)
    compound_score = sentiment['compound']
    
    if compound_score >= 0.05:
        sentiment_label = "Positive"
    elif compound_score <= -0.05:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    # Check for issue keywords and send WhatsApp alert
    check_issue_keywords_and_notify(feedback.text)
    
    return {"text": feedback.text, "sentiment": sentiment_label}

@app.get("/fetch_reddit/{subreddit}")
def fetch_posts(subreddit: str):
    posts = reddit.subreddit(subreddit).hot(limit=100)
    feedback_list = []
    
    for post in posts:
        sentiment = sentiment_analyzer.polarity_scores(post.title)
        compound_score = sentiment['compound']
        sentiment_label = "Neutral"
        if compound_score >= 0.05:
            sentiment_label = "Positive"
        elif compound_score <= -0.05:
            sentiment_label = "Negative"
        
        feedback_list.append({"text": post.title, "sentiment": sentiment_label})
    
    return feedback_list

# Streamlit Frontend
st.title("📊 Event Sentiment Analysis Dashboard")
st.write("Monitor attendee sentiment in real-time")

feedback_text = st.text_area("📝 Enter Feedback:")
if st.button("Submit Feedback"):
    response = requests.post("http://127.0.0.1:8000/analyze", json={"text": feedback_text})
    
    if response.status_code == 200:
        result = response.json()
        st.subheader(f"🧐 Sentiment: {result['sentiment']}")
        
        # Check for issue keywords and send WhatsApp alert
        check_issue_keywords_and_notify(feedback_text)
    else:
        st.write("⚠️ Error analyzing sentiment")

subreddit = st.text_input("🔍 Enter Topic Name:")
if st.button("Fetch Posts"):
    response = requests.get(f"http://127.0.0.1:8000/fetch_reddit/{subreddit}")
    
    if response.status_code == 200:
        posts = response.json()
        df = pd.DataFrame(posts)
        st.write(df)

        # Sentiment Count
        sentiment_counts = df["sentiment"].value_counts()
        total_comments = len(df)
        negative_percentage = (sentiment_counts.get("Negative", 0) / total_comments) * 100

        # Display Negative Comment Percentage
        st.subheader(f"🔴 Negative Comments: {negative_percentage:.2f}% of total feedback")

        # **📊 Visualization Layout**
        col1, col2 = st.columns(2)

        # **📈 Pie Chart - Sentiment Distribution**
        with col1:
            fig1, ax1 = plt.subplots(figsize=(4, 4))
            ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', 
                    colors=['green', 'gray', 'red'], startangle=90)
            ax1.set_title("Sentiment Distribution")
            st.pyplot(fig1)

        # **📊 Bar Chart - Sentiment Counts**
        with col2:
            fig2, ax2 = plt.subplots(figsize=(4, 4))
            sns.barplot(x=sentiment_counts.index, y=sentiment_counts.values, 
                        palette=["green", "gray", "red"], ax=ax2)
            ax2.set_title("Sentiment Counts")
            ax2.set_ylabel("Number of Comments")
            st.pyplot(fig2)

        # **🔹 Word Cloud for Negative Comments**
        negative_comments = " ".join(df[df["sentiment"] == "Negative"]["text"].tolist())
        if negative_comments:
            fig3, ax3 = plt.subplots(figsize=(8, 4))
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(negative_comments)
            ax3.imshow(wordcloud, interpolation="bilinear")
            ax3.axis("off")
            st.subheader("⚠️ Common Words in Negative Comments")
            st.pyplot(fig3)

        # **📊 Line Chart for Sentiment Trends**
        df["sentiment_score"] = df["sentiment"].map({"Positive": 1, "Neutral": 0, "Negative": -1})
        df["cumulative_sentiment"] = df["sentiment_score"].cumsum()
        
        fig4, ax4 = plt.subplots(figsize=(6, 3))
        sns.lineplot(data=df, x=df.index, y="cumulative_sentiment", marker="o", ax=ax4)
        ax4.set_title("📈 Sentiment Trend Over Time")
        ax4.set_ylabel("Cumulative Sentiment Score")
        ax4.set_xlabel("Comments Index")
        st.pyplot(fig4)

    else:
        st.write("⚠️ Error fetching posts")

# Running Backend
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
