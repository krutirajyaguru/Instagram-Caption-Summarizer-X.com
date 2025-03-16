import psycopg2
import requests
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, PegasusTokenizer
from requests_oauthlib import OAuth1
import logging
from datetime import datetime
import os
import re
from config import tokens
from PIL import Image
from io import BytesIO

# Import setup_logging from utils
from utils import setup_logging

class InstagramCaptionSummarizer:
    """
    A class to handle the summarization of Instagram captions and posting them to Twitter.

    Attributes:
        log_dir (str): Directory for storing log files.
        LOG_FILE_PATH (str): Path to the log file.
        DB_CONFIG (dict): PostgreSQL connection configuration.
        API_KEY (str): API key for Twitter authentication.
        API_SECRET_KEY (str): API secret key for Twitter authentication.
        ACCESS_TOKEN (str): Access token for Twitter authentication.
        ACCESS_TOKEN_SECRET (str): Access token secret for Twitter authentication.
        POST_TWEET_URL (str): URL to post tweets on Twitter.
        UPLOAD_MEDIA_URL (str): URL to upload media on Twitter.
        tokenizer (PegasusTokenizer): Tokenizer for the Pegasus model.
        model (AutoModelForSeq2SeqLM): Pre-trained model for caption summarization.
    """
    
    def __init__(self):
        """
        Initializes the InstagramCaptionSummarizer class with configuration values.
        """
        self.log_dir = "logs"
        self.LOG_FILE_PATH = os.path.join(self.log_dir, f"log_{datetime.today().strftime('%Y-%m-%d')}.log")
        
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

        # Initialize logging
        setup_logging(self.log_dir)

        # Initialize the tokenizer and model for caption summarization
        self.tokenizer = PegasusTokenizer.from_pretrained("google/pegasus-cnn_dailymail")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("google/pegasus-cnn_dailymail")

    def get_latest_post(self):
        """
        Fetches the latest Instagram post caption and image from the database.

        Returns:
            tuple: A tuple containing the Instagram caption and image URL (if available).
        """
        try:
            with psycopg2.connect(**self.DB_CONFIG) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT caption, image_url FROM instagram_posts
                        ORDER BY created_at DESC
                        LIMIT 1;
                    """)
                    post = cursor.fetchone()
                    logging.info("Successfully fetched latest post from database.")
                    return post if post else (None, None)
        except Exception as e:
            logging.error(f"Error fetching post from PostgreSQL: {e}")
            return (None, None)

    def summarize_caption(self, caption):
        """
        Summarizes the Instagram caption using the pre-trained Pegasus model.

        Args:
            caption (str): The Instagram caption to summarize.

        Returns:
            str: The summarized caption.
        """
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
            # Filter out unwanted tokens and clean the summary
            summary = summary.replace('<n>', '').replace('<pad>', '').strip()

            # If summary exceeds Twitter character limit, clean up
            if len(summary) > 280:
                summary = self.clean_incomplete_sentence(summary[:280])

            logging.info("Caption successfully summarized.")
            return summary
        except Exception as e:
            logging.error(f"Error summarizing caption: {e}")
            return None

    def clean_incomplete_sentence(self, text):
        """
        Cleans up an incomplete sentence to end at a punctuation mark.

        Args:
            text (str): The text to clean.

        Returns:
            str: The cleaned text.
        """
        match = re.search(r'([.!?])[^.!?]*$', text)
        if match:
            return text[:match.start(1) + 1]
        return text

    def upload_image_from_url(self, image_url):
        """
        Uploads an image from a URL to Twitter.

        Args:
            image_url (str): The URL of the image to upload.

        Returns:
            str: The media ID of the uploaded image.
        """
        try:
            auth = OAuth1(self.API_KEY, self.API_SECRET_KEY, self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)

            response = requests.get(image_url)
            img_byte_array = BytesIO(response.content)
            files = {"media": img_byte_array.getvalue()}

            media_upload = requests.post(self.UPLOAD_MEDIA_URL, auth=auth, files=files)

            if media_upload.status_code == 200:
                media_id = media_upload.json()["media_id_string"]
                logging.info("Image uploaded successfully")
                return media_id
            else:
                logging.error(f"Failed to upload image: {media_upload.text}")
                return None
        except Exception as e:
            logging.error(f"Error uploading image from URL: {e}")
            return None

    def post_tweet(self, tweet_text, image_url):
        """
        Posts a tweet with or without an image to Twitter.

        Args:
            tweet_text (str): The text of the tweet.
            image_url (str, optional): The URL of the image to post with the tweet.

        Returns:
            dict: The response JSON from Twitter's API, if successful.
        """
        try:
            auth = OAuth1(self.API_KEY, self.API_SECRET_KEY, self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)
            payload = {"text": tweet_text}

            if image_url:
                media_id = self.upload_image_from_url(image_url)
                if media_id:
                    payload["media"] = {"media_ids": [media_id]}

            response = requests.post(self.POST_TWEET_URL, auth=auth, json=payload)

            if response.status_code == 201:
                logging.info("Tweet posted successfully")
                return response.json()
            else:
                logging.error(f"Failed to post tweet: {response.text}")
                return None
        except Exception as e:
            logging.error(f"Error posting tweet: {e}")
            return None

if __name__ == "__main__":
    # You can create a sample test here if needed.
    pass
