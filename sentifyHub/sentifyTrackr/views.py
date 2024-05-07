from django.shortcuts import render
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import tensorflow as tf
from tensorflow import keras
import pickle
import logging
from urllib.parse import urlparse, parse_qs
import torch
from torch.nn.functional import sigmoid
from transformers import DistilBertTokenizer
from .model import DistilBERTClass
import pandas as pd
import json
import webbrowser
import os
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse

# Load environment variables
load_dotenv()
api_key = os.getenv('API_KEY')

# YouTube API Client
youtube = build('youtube', 'v3', developerKey=api_key)

# Global variables
dic = {'toxic': 0, 'severe_toxic': 0, 'obscene': 0, 'threat': 0, 'insult': 0, 'identity_hate': 0, 'good': 0}
MAX_FEATURES = 20000
loaded_vocab = None


with open('/Users/manojkumarkolli/Documents/RealTimeProjects/live_sentiment/string_lookup_vocabulary.pkl', 'rb') as file:
    loaded_vocab = pickle.load(file)

# Load the PyTorch model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = '/Users/manojkumarkolli/Documents/RealTimeProjects/live_sentiment/sentifyHub/sentifyTrackr/distilbert_bilstm_model.pth'
pytorch_model = DistilBERTClass().to(device)
pytorch_model.load_state_dict(torch.load(model_path, map_location=device))
pytorch_model.eval()
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

def extract_channel_id(video_id):
    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )
    response = request.execute()
    # print(response)

    # Extract category ID from the response
    if 'items' in response and len(response['items']) > 0:
        channel_id = response['items'][0]['snippet']['channelId']
        # Make API request to get category details
        return channel_id
    return None

def get_latest_videos(channel_id, max_results=20):
    # Make API request to get the latest videos uploaded by the channel
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        order='date',
        type='video',
        maxResults=max_results
    )
    response = request.execute()
    # print(response)
    videos = []
    for item in response['items']:
        video_id = item['id']['videoId']
        video_title = item['snippet']['title']
        videos.append({'video_id': video_id, 'title': video_title})
    return videos

def get_video_genre(video_id):
    # Make API request to get video details
    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )
    response = request.execute()
    # Extract category ID from the response
    if 'items' in response and len(response['items']) > 0:
        category_id = response['items'][0]['snippet']['categoryId']
        # Make API request to get category details
        category_request = youtube.videoCategories().list(
            part='snippet',
            id=category_id
        )
        category_response = category_request.execute()
        if 'items' in category_response and len(category_response['items']) > 0:
            genre_name = category_response['items'][0]['snippet']['title']
            return genre_name
    return None


def get_video_statistics(video_id):
    # Make API request to get video statistics (like view count)
    request = youtube.videos().list(
        part='statistics',
        id=video_id
    )
    response = request.execute()
    if 'items' in response and len(response['items']) > 0:
        statistics = response['items'][0]['statistics']
        view_count = int(statistics.get('viewCount', 0))
        return view_count
    return 0

def video_metrics(request):
    with open('video_metrics.json', 'r') as file:
        data = json.load(file)
    return JsonResponse(data)

def recommend_genre(request):
    channel_id = request.GET.get('channel_id')
    if not channel_id:
        return JsonResponse({'error': 'Channel ID is required'}, status=400)

    try:
        with open('video_metrics.json', 'r') as file:
            data = json.load(file)
        
        if channel_id not in data:
            return JsonResponse({'error': 'Channel data not found'}, status=404)

        # Example analysis logic to determine the recommended genre
        genre_scores = {}
        for video in data[channel_id]:
            genre = video.get('genre')
            views = video.get('views', 0)
            if genre in genre_scores:
                genre_scores[genre] += views
            else:
                genre_scores[genre] = views

        recommended_genre = max(genre_scores, key=genre_scores.get)  # Pick the genre with the highest views
        return JsonResponse({'recommended_genre': recommended_genre})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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

def save_data_to_db(channel_id, video_id, views, metrics, genre):
    file_path = 'video_metrics.json'
    data = {}

    # Check if the file already exists and read its content
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)

    # Check if the channel ID already exists in the data
    if channel_id in data:
        # Append the new video data to the existing list for the channel
        metric = data[channel_id]
        flag = True
        for record in metric:
            if record["youtube_url_id"] == video_id:
                record["views"] = views
                record["metrics"] = metrics
                record["genre"] = genre
                flag = False
                break 
        if flag:
            data[channel_id].append({'youtube_url_id': video_id, 'views': views, 'metrics': metrics, 'genre': genre})
    else:
        # Create a new list for the new channel ID with the video data
        data[channel_id] = [{'youtube_url_id': video_id, 'views': views, 'metrics': metrics, 'genre': genre}]

    # Write the updated data back to the file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
    print("File saved successfully")



def get_metrics(data):
    df = pd.DataFrame(data)

    # Summing up the values for each column
    metrics = df.sum().to_dict()

    return metrics

# def home(request):
#     if request.method=="POST":
#         video_url=request.POST.get('video_url')

#         # channel_id = extract_channel_id(
#         #     get_video_id_from_url(video_url)
#         # )
#         # latest_videos = get_latest_videos(channel_id)
#         # genre_reach = {}
#         # for video in latest_videos:
#         #     video_id = video['video_id']
#         #     genre = get_video_genre(video_id)

#         #     c = 0
#         #     print(genre)
#         #     if genre:
#         #         c += 1
#         #         sentiment_counts = get_video_sentiment(c)
#         #         view_count = get_video_statistics(video_id)
#         #         weighted_reach = view_count * (
#         #                     sentiment_counts['good'] / (sentiment_counts['good'] + sentiment_counts['toxic']))
#         #         if genre in genre_reach:
#         #             genre_reach[genre] += weighted_reach
#         #         else:
#         #             genre_reach[genre] = weighted_reach

#         video_id = get_video_id_from_url(video_url)
#         response = youtube.commentThreads().list(
#             part="snippet",
#             videoId=video_id,
#             textFormat="plainText",
#             maxResults=10
#         ).execute()

#         classified_comments = []
#         predicted_data = []
#         for item in response.get('items', []):
#             comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay']
#             # flags = predict(comment_text)
#             flags = predict_with_pytorch(comment_text)
#             predicted_data.append(flags)
#             classified_comments.append({"text": comment_text, "flags": flags})
#         metrics = get_metrics(predicted_data)
#         print(metrics)

#         # Example test comment
#         # test_comment = "I fucking kill u"
#         # classified_comments.append({"text": test_comment, "flags": predict(test_comment)})

#         return render(request, 'chart.html', {'comments': classified_comments, "dic": dic})
#     else:
#         return render(request,'home.html')

def home(request):
    if request.method == "POST":
        video_url = request.POST.get('video_url')
        video_id = get_video_id_from_url(video_url)
        if video_id:
            channel_id = extract_channel_id(video_id)
            if channel_id:
                latest_videos = get_latest_videos(channel_id)
                all_video_metrics = []

                for video in latest_videos:
                    video_id = video['video_id']
                    views = get_video_statistics(video_id)
                    genre = get_video_genre(video_id)

                    # Process comments for each video
                    response = youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        textFormat="plainText",
                        maxResults=100  # You can adjust the maxResults as needed
                    ).execute()

                    classified_comments = []
                    predicted_data = []
                    for item in response.get('items', []):
                        comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay']
                        flags = predict_with_pytorch(comment_text)
                        predicted_data.append(flags)
                        classified_comments.append({"text": comment_text, "flags": flags})
                    metrics = get_metrics(predicted_data)

                    # Append combined data for the current video
                    video_details = {
                        'video_id': video_id,
                        'views': views,
                        'metrics': metrics,
                        'comments': classified_comments,
                        'genre': genre
                    }
                    all_video_metrics.append(video_details)

                    # Save data to JSON for each video
                    save_data_to_db(channel_id, video_id, views, metrics, genre)

                # Render results
                webbrowser.open('http://localhost:8501')
                return HttpResponse("Status 200")
                # return render(request, 'chart.html', {'videos': all_video_metrics, 'channel_id': channel_id})
            else:
                return HttpResponse("Channel ID not found.", status=404)
        else:
            return HttpResponse("Invalid YouTube URL.", status=400)
    else:
        return render(request, 'home.html')


def predict(comment):
    global dic
    try:
        vec = keras.layers.TextVectorization(max_tokens=MAX_FEATURES, output_sequence_length=1800, output_mode='int')
        model = keras.models.load_model('/Users/manojkumarkolli/Documents/RealTimeProjects/live_sentiment/toxicity.h5')
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

def predict_with_pytorch(comment):
    global dic
    try:
        inputs = tokenizer(comment, return_tensors="pt", padding=True, truncation=True, max_length=512)
        input_ids = inputs['input_ids'].to(device)
        attention_mask = inputs['attention_mask'].to(device)
        with torch.no_grad():
            outputs = pytorch_model(input_ids, attention_mask)
        probabilities = sigmoid(outputs).squeeze().tolist()

        labels = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
        flags = {label: prob > 0.5 for label, prob in zip(labels, probabilities)}
        flags['good'] = all(not val for val in flags.values())

        # Update global counters
        for flag, value in flags.items():
            if value:
                dic[flag] += 1

        return flags
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return {col: False for col in ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate', 'good']}
