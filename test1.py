from googleapiclient.discovery import build
import re
#api_key="AIzaSyDEZyllKXrEnR-58tzzkOE8JNPQg5YiiRk"

from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import os
# Set up the YouTube Data API
load_dotenv()
api_key = os.getenv('API_KEY')
youtube = build('youtube', 'v3', developerKey=api_key)



def extract_channel_id(video_id):
    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )
    response = request.execute()
    #print(response)
    
    # Extract category ID from the response
    if 'items' in response and len(response['items']) > 0:
        channel_id = response['items'][0]['snippet']['channelId']
        # Make API request to get category details
        return channel_id
    return None

def get_latest_videos(channel_id, max_results=10):
    # Make API request to get the latest videos uploaded by the channel
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        order='date',
        type='video',
        maxResults=max_results
    )
    response = request.execute()
    #print(response)
    videos = []
    for item in response['items']:
        video_id = item['id']['videoId']
        video_title = item['snippet']['title']
        videos.append({'video_id': video_id, 'title': video_title})
    print(videos)
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

# Example usage
channel_id = extract_channel_id(get_video_id_from_url("https://www.youtube.com/watch?v=OKWrfVSE0fE&ab_channel=Prasadtechintelugu"))
#'UCijVIIfFzspulKc7yWA2Qhg'
#print(channel_id)
latest_videos = get_latest_videos(channel_id)
genre_reach = {}

#print(latest_videos)
def get_video_sentiment(c):
    if c%2==0:
        return {'good': 1819, 'toxic': 100, 'non-toxic': 60}
    else:
        return {'good': 1200, 'toxic': 500, 'non-toxic': 10}

for video in latest_videos:
    video_id = video['video_id']
    genre = get_video_genre(video_id)
    
    c=0
    print(genre)
    if genre:
        c+=1
        #here give to the model to get statsics 
        sentiment_counts = get_video_sentiment(c)
        view_count = get_video_statistics(video_id)
        weighted_reach = view_count * (sentiment_counts['good'] / (sentiment_counts['good'] + sentiment_counts['toxic']))
        if genre in genre_reach:
            genre_reach[genre] += weighted_reach
        else:
            genre_reach[genre] = weighted_reach

# Find the genre with the maximum reach
max_reach_genre = max(genre_reach, key=genre_reach.get)
max_reach = genre_reach[max_reach_genre]

print("Genre with Maximum Reach:", max_reach_genre)
print("Maximum Reach:", max_reach)
