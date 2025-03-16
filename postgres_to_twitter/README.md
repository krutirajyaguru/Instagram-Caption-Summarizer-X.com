# Instagram Caption Summarizer to Twitter

This Container fetches Instagram captions from a PostgreSQL database, summarizes them using Hugging Face transformer models, and posts the summarized captions to Twitter (X.com) via the Twitter API. The project is implemented using Python and Streamlit for the user interface.

## Overview

- **Instagram Data Fetching:** Retrieves the latest Instagram caption and image from the database.
- **Caption Summarization:** Uses the Hugging Face google/pegasus-cnn_dailymail model to summarize the caption.
- **Twitter Posting:** Posts the summarized caption and image to Twitter.
- **Logging:** Logs all activities and errors to a daily log file for tracking and debugging.

## Set Up Hugging Face API

1. **Create an account on [Hugging Face](https://huggingface.co).**

2. **Generate an API token:**
   - Navigate to *Account Settings > Access Tokens* and create a new token.

3. **Ensure the required packages are installed:**

```bash
pip install transformers torch sentencepiece
```

## Set Up Twitter (X.com) API

1. **Create a Twitter Developer Account:**
   - Sign up at [Twitter Developer Portal](https://developer.x.com/en).

2. **Generate API Credentials:**
   - Go to "Projects and Apps" in the Developer Portal.
   - Select your app and navigate to the *Keys and Tokens* tab.
   - Regenerate and save the following credentials:
     - API Key and Secret: `API_KEY`, `API_SECRET_KEY`
     - Access Token and Secret: `ACCESS_TOKEN`, `ACCESS_TOKEN_SECRET`

3. **Configure User Authentication Settings:**
   - Ensure the app has *Read and Write* permissions and is set to *Web App, Automated App or Bot*.
   - Provide the following:
     - Callback URI: `https://example.com/callback`
     - Website URL: `https://example.com/callback`

   **Note:** Avoid using `https://localhost` as it's not publicly accessible by Twitter servers.



## Files Structure Overview:

- **app.py:** This is the main Streamlit application file. It serves as the interface for the user to interact with the Instagram Caption Summarizer. It fetches the latest caption and image from the PostgreSQL database and allows the user to summarize and post the caption and image to Twitter.

- **summarizer.py:** Contains the logic for summarizing Instagram captions using the Pegasus model and posting summarized captions to Twitter. It also interacts with the PostgreSQL database to fetch captions.

- **config.py:** Stores API credentials for Instagram, PostgreSQL, and Twitter. These credentials are used for connecting to the respective services. It also contains database configuration parameters like host, user, password, and port.

- **utils.py:** Sets up logging to output logs with a daily timestamp and the console, creating the log directory if it doesn't exist. Logs are captured at the INFO level with a specific format.

- **tests - test_summerizer.py:** Contains unit tests for the InstagramCaptionSummarizer class, ensuring it summarizes captions within the Twitter character limit and trims incomplete sentences. Run tests with python -m unittest test.py.

- **Dockerfile:** Defines the instructions to build the Docker image for the project. It installs the necessary dependencies, sets the working directory, and specifies the command to run the Streamlit app.

- **requirements.txt:** Lists all the Python dependencies required to run the application. It includes libraries such as streamlit, transformers, requests, psycopg2, requests_oauthlib, etc.


## Configuration

Ensure you update the `config.py` file with your PostgreSQL and Twitter credentials:

```python
DB_HOST = "your_postgres_host"
DB_NAME = "your_postgres_db"
DB_USER = "your_postgres_user"
DB_PASSWORD = "your_postgres_password"

API_KEY = "your_twitter_api_key"
API_SECRET_KEY = "your_twitter_api_secret"
ACCESS_TOKEN = "your_access_token"
ACCESS_TOKEN_SECRET = "your_access_token_secret"
```


## Check Posted Tweets

If a tweet is posted successfully, you can view it using the following format:

```bash
https://x.com/your_username/status/TWEET_ID
```

## Known Limitations

1. **Streamlit** only controls the width automatically, not the height of the displayed image.

2. **Twitter API Rate Limits (Free Tier):**
   - 1,500 posts per month (at the app level)
   - 50 tweets per 24 hours


