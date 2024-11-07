from fastapi import FastAPI, Request, Form
import uvicorn
import os
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from src.textSummarizer.pipeline.prediction_pipeline import PredictionPipeline
from typing import Optional
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import spacy
from collections import Counter
import re
from datetime import datetime
import json
from translate import Translator

# Download required NLTK data
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory
templates = Jinja2Templates(directory="templates")

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

class TextAnalyzer:
    @staticmethod
    def get_sentiment(text):
        sentiment_scores = sia.polarity_scores(text)
        # Determine overall sentiment
        if sentiment_scores['compound'] >= 0.05:
            sentiment = 'Positive'
        else:
            sentiment = 'Negative'
        
        return {
            'overall': sentiment,
            'scores': sentiment_scores
        }

     # Minimum 1 minute

   

   

   



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.get("/train")
async def training():
    try:
        os.system("python main.py")
        return {"success": True, "message": "Training successful!!"}
    except Exception as e:
        return {"success": False, "error": str(e)}
# (Keep your existing app.py code exactly as it is, with the added functions)









# Update only the summarize endpoint
@app.post("/summarize")
async def summarize(
    request: Request, 
    text: str = Form(...),
    min_length: Optional[int] = Form(30),    
    max_length: Optional[int] = Form(150),    
    language: Optional[str] = Form("en")  # Add language parameter
):
    try:
        analyzer = TextAnalyzer()
        
        analysis = {
            'sentiment': analyzer.get_sentiment(text),
            
        }

        # Pass length parameters to the prediction pipeline
        obj = PredictionPipeline()
        standard_summary = obj.predict(
            text, 
            min_length=min_length, 
            max_length=max_length
        )

        if language != "en":
            translator = Translator(to_lang=language)
            standard_summary = translator.translate(standard_summary)

        summary_formats = {
            "standard": standard_summary,
            
        }

       

        return {
            "success": True, 
            "summary_formats": summary_formats,
            "analysis": analysis
        }
    except Exception as e:
        return {"success": False, "error": str(e)}




if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
