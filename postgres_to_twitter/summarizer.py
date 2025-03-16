import psycopg2
import requests
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, PegasusTokenizer
from requests_oauthlib import OAuth1
import re,logging
from config import tokens
from PIL import Image
from io import BytesIO
from utils import setup_logging # Import setup_logging from utils

class InstagramCaptionSummarizer:
    """
    A class to handle the summarization of Instagram captions and posting them to Twitter.
    """

    def __init__(self):
        """Initializes the InstagramCaptionSummarizer class with configuration values."""
        #self.log_dir = "logs"

        # Initialize logging
        setup_logging()

        # Database configuration
        self.DB_CONFIG = {
            "dbname": "insta_posts_db",
            "user": tokens['user'],
            "password": tokens['password'],
            "host": tokens['host'],
            "port": tokens['port']
        }

        # Twitter API credentials
        self.API_KEY = tokens['api_key']
        self.API_SECRET_KEY = tokens['api_secret_key']
        self.ACCESS_TOKEN = tokens['access_token']
        self.ACCESS_TOKEN_SECRET = tokens['access_token_secret']

        # Twitter API endpoints
        self.POST_TWEET_URL = "https://api.twitter.com/2/tweets"
        self.UPLOAD_MEDIA_URL = "https://upload.twitter.com/1.1/media/upload.json"

        # Initialize the tokenizer and model for caption summarization
        self.tokenizer = PegasusTokenizer.from_pretrained("google/pegasus-cnn_dailymail")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("google/pegasus-cnn_dailymail")

    def get_latest_post(self):
        """Fetches the latest Instagram post caption and image from the database."""
        try:
            with psycopg2.connect(**self.DB_CONFIG) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT caption, image_url FROM instagram_posts
                        ORDER BY created_at DESC
                        LIMIT 1;
                    """)
                    post = cursor.fetchone()
                    return post if post else (None, None)
        except Exception as e:
            logging.error(f"Error fetching post from PostgreSQL: {e}")
            return (None, None)

    def summarize_caption(self, caption):
        """Summarizes the Instagram caption using the pre-trained Pegasus model."""
        try:
            inputs = self.tokenizer(caption, return_tensors="pt", max_length=1024, truncation=True, padding=True)
            summary_ids = self.model.generate(
                inputs['input_ids'],
                max_length=300,
                min_length=100,
                num_beams=4,
                early_stopping=True
            )
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

            # Clean and truncate the summary if needed
            summary = summary.replace('<n>', '').replace('<pad>', '').strip()
            if len(summary) > 280:
                summary = self.clean_incomplete_sentence(summary[:280])

            return summary
        except Exception as e:
            import logging
            logging.error(f"Error summarizing caption: {e}")
            return None

    def clean_incomplete_sentence(self, text):
        """Cleans up an incomplete sentence to end at a punctuation mark."""
        match = re.search(r'([.!?])[^.!?]*$', text)
        if match:
            return text[:match.start(1) + 1]
        return text

    def upload_image_from_url(self, image_url):
        """Uploads an image from a URL to Twitter."""
        try:
            auth = OAuth1(self.API_KEY, self.API_SECRET_KEY, self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)

            response = requests.get(image_url)
            img_byte_array = BytesIO(response.content)
            files = {"media": img_byte_array.getvalue()}

            media_upload = requests.post(self.UPLOAD_MEDIA_URL, auth=auth, files=files)

            if media_upload.status_code == 200:
                return media_upload.json()["media_id_string"]
            else:
                import logging
                logging.error(f"Failed to upload image: {media_upload.text}")
                return None
        except Exception as e:
            import logging
            logging.error(f"Error uploading image from URL: {e}")
            return None

    def post_tweet(self, tweet_text, image_url=None):
        """Posts a tweet with or without an image to Twitter."""
        try:
            auth = OAuth1(self.API_KEY, self.API_SECRET_KEY, self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)
            payload = {"text": tweet_text}

            if image_url:
                media_id = self.upload_image_from_url(image_url)
                if media_id:
                    payload["media"] = {"media_ids": [media_id]}

            response = requests.post(self.POST_TWEET_URL, auth=auth, json=payload)

            if response.status_code == 201:
                return response.json()
            else:
                import logging
                logging.error(f"Failed to post tweet: {response.text}")
                return None
        except Exception as e:
            import logging
            logging.error(f"Error posting tweet: {e}")
            return None

if __name__ == "__main__":
    summarizer = InstagramCaptionSummarizer()
    caption, image_url = summarizer.get_latest_post()
    print(caption,image_url)