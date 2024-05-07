# Live Sentiment Analysis for YouTube Comments

## Overview

This project performs real-time sentiment analysis on YouTube comments provided by the user. It classifies the sentiment of each comment, helping to gauge the overall mood or tone expressed in the comments. The project also provides visualizations of sentiment trends through graphs.

## Features
1. **Real-Time Analysis:** As users provide the YouTube URL, the system promptly retrieves the latest comments associated with the video. Using sentiment analysis techniques, it evaluates the sentiment of each comment in real-time, allowing users to see the sentiment distribution as comments are processed.

2. **User-Friendly Interface:** The interface is designed with simplicity in mind. Users input the YouTube URL into a designated field, and the system handles the rest. Clear instructions guide users through the process, ensuring a seamless experience for users of all levels of technical proficiency.

3. **Sentiment Classification:** Comments are swiftly categorized into good,toxic,threat,obsence and insult. Additionally, the system identifies toxic comments containing abusive language, hate speech, or obscenities, allowing for efficient content moderation.

4. **Practical Applications:** This tool serves various practical purposes, such as understanding public sentiment towards the video's content, facilitating content moderation by flagging harmful comments, and providing valuable insights for creators and marketers to optimize their strategies.

5. **Retrieval of Comments and Video Information:** The system retrieves the latest 100 comments associated with the provided YouTube video URL. It also extracts essential metadata such as the channel ID, video ID, and view count, providing context for the sentiment analysis and recommendations.

6. **Recommendations Based on Video Content:** Leveraging the analyzed comments and video metadata, the system generates recommendations tailored to the video's content. These recommendations may include related videos, channels, or topics of interest to enhance user engagement and retention.

7. **Visualization of Sentiment Trends:** The system presents visualizations such as line graphs or pie charts to illustrate sentiment trends over time. Users can observe how the sentiment of comments evolves throughout the video's duration, enabling them to gain insights into audience reactions and engagement patterns.


## SetUp and Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/ManojKumarKolli/LiveSentiment.git
   cd LiveSentiment
   ```
2. **Make the shell script executable**
   ```bash
   chmod +x run_script.sh
   ```
3. **Run the shell Scipt**
   ```bash
   ./run_script.sh
   ```
4. **Run the Streamlit Application**
   ```bash
   streamlit run video_metrics_function.py
   ```

