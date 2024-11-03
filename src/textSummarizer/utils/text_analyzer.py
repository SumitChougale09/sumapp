import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk import FreqDist
from nltk.tokenize import word_tokenize, sent_tokenize
import spacy

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('vader_lexicon')

class TextAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def get_sentiment(self, text):
        """Analyze sentiment of the text."""
        scores = self.sentiment_analyzer.polarity_scores(text)
        return {
            "overall": "Positive" if scores['compound'] > 0 else "Negative" if scores['compound'] < 0 else "Neutral",
            "scores": scores
        }

    def get_reading_time(self, text):
        """Estimate reading time in minutes."""
        words = len(word_tokenize(text))
        reading_speed = 200  # Average reading speed in words per minute
        return round(words / reading_speed)

    def get_key_phrases(self, text):
        """Extract key phrases from the text using spaCy."""
        doc = self.nlp(text)
        return [chunk.text for chunk in doc.noun_chunks]

    def get_text_stats(self, text):
        """Get basic statistics about the text."""
        words = word_tokenize(text)
        sentences = sent_tokenize(text)
        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            "complexity_score": self.calculate_complexity(words)
        }

    def calculate_complexity(self, words):
        """Calculate a simple complexity score based on unique words."""
        unique_words = set(words)
        return len(unique_words) / len(words) * 10 if words else 0

    def extract_topics(self, text):
        """Extract topics from the text using spaCy."""
        doc = self.nlp(text)
        topics = []
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'GPE', 'PERSON', 'PRODUCT']:
                topics.append((ent.text, ent.label_))
        return topics