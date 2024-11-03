from src.textSummarizer.config.configuration import ConfigurationManager
from transformers import AutoTokenizer
from transformers import pipeline


class PredictionPipeline:
    def __init__(self):
        self.config = ConfigurationManager().get_model_evaluation_config()
    
    def predict(self, text, min_length=30, max_length=150):
        tokenizer = AutoTokenizer.from_pretrained(self.config.tokenizer_path)
        
        # Update generation kwargs with min and max length
        gen_kwargs = {
            "length_penalty": 0.8, 
            "num_beams": 8, 
            "max_length": max_length,
            "min_length": min_length,
            "no_repeat_ngram_size": 2,  # Prevent repetition of phrases
            "early_stopping": True      # Stop when suitable generation is found
        }

        pipe = pipeline("summarization", model=self.config.model_path, tokenizer=tokenizer)

        print("Dialogue:")
        print(text)

        output = pipe(text, **gen_kwargs)[0]["summary_text"]
        print("\nModel Summary:")
        print(output)

        return output