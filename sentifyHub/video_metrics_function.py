import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import webbrowser

API_URL = "http://localhost:8000/api/video-metrics/"


def load_data():
    response = requests.get(API_URL)
    data = response.json()
    return data


def plot_sentiment_trends(metrics_df):
    fig = px.line(metrics_df, labels={'value': 'Count', 'variable': 'Sentiment Type'})
    fig.update_layout(title="Sentiment Trends Over Time", xaxis_title="Videos", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)


def plot_view_distribution(videos_df):
    fig = px.bar(videos_df, x='youtube_url_id', y='views')
    fig.update_layout(title="Views Distribution Across Videos", xaxis_title="Video ID", yaxis_title="Views",
                      xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig, use_container_width=True)


def display_video_metrics(videos):
    metrics_df = pd.DataFrame([v['metrics'] for v in videos])
    videos_df = pd.DataFrame(videos)

    st.write("Total Views Across All Videos:", videos_df['views'].sum())
    st.write("Average Views Per Video:", np.mean(videos_df['views']))

    plot_view_distribution(videos_df)
    plot_sentiment_trends(metrics_df)


def show_genre_distribution(videos_df):
    genre_counts = videos_df['genre'].value_counts()
    plt.figure(figsize=(10, 5))
    sns.barplot(x=genre_counts.index, y=genre_counts.values)
    plt.title("Genre Distribution")
    plt.xlabel("Genre")
    plt.ylabel("Number of Videos")
    st.pyplot(plt)


def display_video_metrics(videos):
    metrics_df = pd.DataFrame([v['metrics'] for v in videos])
    videos_df = pd.DataFrame(videos)
    videos_df['metrics'] = metrics_df.sum(axis=1)  # Assuming metrics are summable

    st.write("Total Views Across All Videos:", videos_df['views'].sum())
    st.write("Average Views Per Video:", np.mean(videos_df['views']))

    plot_view_distribution(videos_df)
    plot_sentiment_trends(metrics_df)
    show_genre_distribution(videos_df)


def update_video_metrics(video_id):
    update_url = f"http://127.0.0.1:8000/classify/?video_id={video_id}"
    response = requests.get(update_url)
    if response.status_code == 200:
        st.success("Video data updated successfully!")
    else:
        st.error(f"Failed to update video data: {response.text}")

def get_genre_recommendation(channel_id):
    recommendation_url = f"http://127.0.0.1:8000/api/recommend-genre/?channel_id={channel_id}"
    response = requests.get(recommendation_url)
    if response.status_code == 200:
        return response.json()['recommended_genre']
    else:
        st.error(f"Failed to fetch genre recommendation: {response.text}")
        return None


def main():
    st.sidebar.title("Navigation")
    if st.sidebar.button("Go to Classification Page"):
        # This link will open in a new tab
        webbrowser.open("http://127.0.0.1:8000/classify/")
        # st.sidebar.markdown(f'<a href="http://127.0.0.1:8000/classify/" target="_blank">Go to Classification Page</a>', unsafe_allow_html=True)

    st.title("YouTube Video Metrics Dashboard")

    data = load_data()

    channel_id = st.selectbox("Select a Channel ID", list(data.keys()), key='channel_id')
    if channel_id:
        videos = data[channel_id]
        video_id = st.selectbox("Select a Video ID", [v['youtube_url_id'] for v in videos], key='video_id')

        selected_video = next((item for item in videos if item['youtube_url_id'] == video_id), None)
        if selected_video:
            st.write("Views:", selected_video['views'])
            st.write("Metrics:")
            st.json(selected_video['metrics'])

            if st.button("Update Video Metrics"):
                update_video_metrics(video_id)

            if st.button("Get Recommendation"):
                recommended_genre = get_genre_recommendation(channel_id)
                if recommended_genre:
                    st.write(f"The recommended genre to enhance channel growth is {recommended_genre}.")

        if st.button("Show Summary for All Videos in Channel"):
            display_video_metrics(videos)

if __name__ == "__main__":
    main()

