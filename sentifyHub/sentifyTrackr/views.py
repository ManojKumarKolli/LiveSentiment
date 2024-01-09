from django.shortcuts import render
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import tensorflow as tf
from tensorflow import keras
import pickle
import logging
from urllib.parse import urlparse, parse_qs


# Load environment variables
load_dotenv()
api_key = os.getenv('API_KEY')

# YouTube API Client
youtube = build('youtube', 'v3', developerKey=api_key)

# Global variables
dic = {'toxic': 0, 'severe_toxic': 0, 'obscene': 0, 'threat': 0, 'insult': 0, 'identity_hate': 0, 'good': 0}
MAX_FEATURES = 20000
loaded_vocab = None


with open('string_lookup_vocabulary.pkl', 'rb') as file:
    loaded_vocab = pickle.load(file)

def get_video_id_from_url(url):
    """
    Extracts the YouTube video ID from a URL.
    """
    # Parsing the URL
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        # URL is a shortened YouTube URL, e.g., https://youtu.be/dQw4w9WgXcQ
        return parsed_url.path[1:]
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        # URL is a full YouTube URL
        query_string = parse_qs(parsed_url.query)
        video_id = query_string.get('v')
        if video_id:
            return video_id[0]
    return None  # In case of an unrecognized format

def home(request):
    if request.method=="POST":
        video_url=request.POST.get('video_url')
        video_id = get_video_id_from_url(video_url)
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            maxResults=2
        ).execute()

        classified_comments = []
        for item in response.get('items', []):
            comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay']
            flags = predict(comment_text)
            classified_comments.append({"text": comment_text, "flags": flags})

        # Example test comment
        #test_comment = "I fucking kill u"
        #classified_comments.append({"text": test_comment, "flags": predict(test_comment)})

        return render(request, 'chart.html', {'comments': classified_comments, "dic": dic})
    else:
        return render(request,'home.html')


def predict(comment):
    global dic
    try:
        vec = keras.layers.TextVectorization(max_tokens=MAX_FEATURES, output_sequence_length=1800, output_mode='int')
        model = keras.models.load_model('toxicity.h5')
        vec.adapt(loaded_vocab)
        vectorized_comment = vec([comment])
        results = model.predict(vectorized_comment)

        flags = {col: results[0][idx] > 0.5 for idx, col in enumerate(['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate'])}
        flags['good'] = all(not flag for flag in flags.values())

        # Update global counters
        for flag, value in flags.items():
            if value:
                dic[flag] += 1

        return flags
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return {col: False for col in ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate', 'good']}
