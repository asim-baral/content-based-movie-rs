import os
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import pickle
import pandas as pd

import requests

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


app = FastAPI()
movies_list = pickle.load((open('movies.pkl', 'rb')))
similarityVector = pickle.load((open('similarityVector.pkl', 'rb')))
similarityVectorTFIDF = pickle.load((open('similarityVectorTFIDF.pkl', 'rb')))
similarityVectorTransformer = pickle.load((open('similarityVectorTransformer.pkl', 'rb')))


# Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/tmdb/find")
def tmdb_find(imdb_id: str):
    url = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={TMDB_API_KEY}&external_source=imdb_id"
    response = requests.get(url)
    return response.json()

@app.get("/search")
def search_movie(query: str):
    movies = movies_list['original_title']
    results = [m for m in movies if query.lower() in m.lower()]
    if  results:
        return{"results":results[:max(len(results)-1, 10)]}
    return []

@app.get("/recommend")
def recommend(recId:int,title: str):
    index = movies_list[ movies_list['original_title']==title ].index[0]
    
    if recId==1:
        distances = list(enumerate(similarityVector[index]))
    elif recId==2:
        distances = list(enumerate(similarityVectorTFIDF[index]))
    elif recId==3:
        distances = list(enumerate(similarityVectorTransformer[index]))


    
    distances.sort(reverse=True, key=lambda x:x[1])
    recommended = distances[0:15]
    
    recommendedIdTitle = []
    for i,l in recommended:
        recommendedIdTitle.append( (movies_list.iloc[i].imdb_id,  movies_list.iloc[i].original_title) )
    return recommendedIdTitle