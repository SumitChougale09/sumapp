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
        elif sentiment_scores['compound'] <= -0.05:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        return {
            'overall': sentiment,
            'scores': sentiment_scores
        }

    @staticmethod
    def get_reading_time(text):
        words = len(text.split())
        reading_time = round(words / 200)  # Average reading speed of 200 words per minute
        return max(1, reading_time)  # Minimum 1 minute

    @staticmethod
    def get_key_phrases(text):
        doc = nlp(text)
        noun_phrases = []
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2:  # Only phrases with 2 or more words
                noun_phrases.append(chunk.text)
        return list(set(noun_phrases))[:5]  # Return top 5 unique phrases

    @staticmethod
    def get_text_stats(text):
        words = len(text.split())
        sentences = len(nltk.sent_tokenize(text))
        blob = TextBlob(text)
        return {
            'word_count': words,
            'sentence_count': sentences,
            'avg_sentence_length': round(words/sentences if sentences > 0 else 0, 1),
            'complexity_score': round(blob.sentiment.subjectivity * 10, 1)  # 0-10 scale
        }

    @staticmethod
    def extract_topics(text):
        doc = nlp(text)
        words = [token.text for token in doc if not token.is_stop and token.is_alpha]
        return Counter(words).most_common(5)

def save_summary_history(original_text, summary, analysis):
    try:
        history_file = "summary_history.json"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_entry = {
            "timestamp": current_time,
            "original_length": len(original_text),
            "summary_length": len(summary),
            "compression_ratio": round((1 - len(summary)/len(original_text)) * 100, 1),
            "sentiment": analysis['sentiment']['overall'],
            "key_topics": analysis['topics'],
            "reading_time": analysis['reading_time']
        }

        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []

        history.append(new_entry)
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=4)

    except Exception as e:
        print(f"Error saving history: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/history")
async def get_history():
    try:
        with open("summary_history.json", 'r') as f:
            history = json.load(f)
        return {"success": True, "history": history}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/train")
async def training():
    try:
        os.system("python main.py")
        return {"success": True, "message": "Training successful!!"}
    except Exception as e:
        return {"success": False, "error": str(e)}
# (Keep your existing app.py code exactly as it is, with the added functions)

def generate_bullet_points(text, summary):
    sentences = summary.split('.')
    return [s.strip() for s in sentences if s.strip()]

def generate_social_post(summary):
    if len(summary) > 280:
        return summary[:277] + "..."
    return summary

def generate_headline(summary):
    first_sentence = summary.split('.')[0]
    return first_sentence if len(first_sentence) < 100 else first_sentence[:97] + "..."




# Update only the summarize endpoint
@app.post("/summarize")
async def summarize(
    request: Request, 
    text: str = Form(...),
    min_length: Optional[int] = Form(30),    # Default minimum length
    max_length: Optional[int] = Form(150)    # Default maximum length
):
    try:
        analyzer = TextAnalyzer()
        
        analysis = {
            'sentiment': analyzer.get_sentiment(text),
            'reading_time': analyzer.get_reading_time(text),
            'key_phrases': analyzer.get_key_phrases(text),
            'stats': analyzer.get_text_stats(text),
            'topics': [topic[0] for topic in analyzer.extract_topics(text)]
        }

        # Pass length parameters to the prediction pipeline
        obj = PredictionPipeline()
        standard_summary = obj.predict(
            text, 
            min_length=min_length, 
            max_length=max_length
        )

        summary_formats = {
            "standard": standard_summary,
            "bullet_points": generate_bullet_points(text, standard_summary),
            "social_post": generate_social_post(standard_summary),
            "headline": generate_headline(standard_summary)
        }

        save_summary_history(text, standard_summary, analysis)

        return {
            "success": True, 
            "summary_formats": summary_formats,
            "analysis": analysis
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)