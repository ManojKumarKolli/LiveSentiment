from django.shortcuts import render
from django.http import HttpResponse
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import tensorflow as tf 
from tensorflow import keras
import pickle
# from tensorflow.python.keras.layers import TextVectorization
# from tensorflow.python.keras.models import load_model
# from tensorflow.python.keras.layers import Bidirectional


load_dotenv()

with open('string_lookup_vocabulary.pkl', 'rb') as file:
            loaded_vocab = pickle.load(file)
# Create your views here.
            
dic={'toxic': 0, 'severe_toxic': 0, 'obscene': 0, 'threat': 0, 'insult': 0, 'identity_hate': 0, 'good': 0}

def home(request):
    api_key = os.getenv('API_KEY')
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Build the YouTube client
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Fetch comments
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

    # Render in a template
    return render(request, 'chart.html', {'comments': comments, "dic": dic})


def predict(comment):
    global loaded_vocab
    MAX_FEATURES=20000
    try:
        #print(comment)
        vec=keras.layers.TextVectorization(max_tokens=MAX_FEATURES,
                                output_sequence_length=1800,
                                output_mode='int')
        model = keras.models.load_model('toxicity.h5')
        print(comment)
        vec.adapt(loaded_vocab)
        vectorized_comment = vec([comment])
        results = model.predict(vectorized_comment)
        # print(results)
        text = ''
        columns=['toxic','severe_toxic','obscene','threat','insult','identity_hate']
        flag=True
        for idx, col in enumerate(columns):
            if results[0][idx]>0.5:
                dic[col]+=1
                flag=False
            text += '{}: {} '.format(col, results[0][idx]>0.5)
        if flag:
             dic['good']+=1
        print(text)
        print(dic)
        

    except Exception as e :
        print("eyyyy",e)
        pass
        
    
    


