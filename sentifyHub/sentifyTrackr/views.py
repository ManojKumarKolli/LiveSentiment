from django.shortcuts import render
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import tensorflow as tf
from tensorflow import keras
import pickle
import logging

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

def home(request):
    response = youtube.commentThreads().list(
        part="snippet",
        videoId="5EuqYVGz_ow",
        textFormat="plainText",
        maxResults=2
    ).execute()
    comments = []
    for item in response.get('items', []):
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        predict(comment)
        comments.append(comment)
    predict("I fucking hate u ")
    comments.append("I fucking hate u ")

    return render(request, 'chart.html', {'comments': comments, "dic": dic})

def predict(comment):
    try:
        vec = keras.layers.TextVectorization(max_tokens=MAX_FEATURES, output_sequence_length=1800, output_mode='int')
        model = keras.models.load_model('toxicity.h5')
        vec.adapt(loaded_vocab)
        vectorized_comment = vec([comment])
        results = model.predict(vectorized_comment)
        text = ''
        columns = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
        flag = True
        for idx, col in enumerate(columns):
            if results[0][idx] > 0.5:
                dic[col] += 1
                flag = False
            text += '{}: {} '.format(col, results[0][idx] > 0.5)
        if flag:
            dic['good'] += 1
    except Exception as e:
        logging.error(f"Prediction error: {e}")
