from django.shortcuts import render
from django.http import HttpResponse
import tweepy
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

# Create your views here.

def home(request):
    api_key = os.getenv('API_KEY')
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Build the YouTube client
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Fetch comments
    response = youtube.commentThreads().list(
        part="snippet",
        videoId="qLxpDE89lfw",
        textFormat="plainText",
        maxResults=100  # Adjust as needed
    ).execute()

    comments = []
    for item in response.get('items', []):
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments.append(comment)

    # Render in a template
    return render(request, 'home.html', {'comments': comments})
    

