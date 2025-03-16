# Instagram Scraper & PostgreSQL Storage

This container scrape Instagram post data and store it in a PostgreSQL database. This project uses Selenium for web scraping and handles dynamic content extraction while ensuring data integrity with duplicate checking.

## Overview

- **Automated Instagram Login:** Logs in using valid Instagram credentials.
- **Profile Scraping:** Navigates to a specified Instagram profile (default: BBC News).
- **Post Data Extraction:** Collects captions and image URLs from Instagram posts.
- **Database Storage:** Stores scraped data in a PostgreSQL database while avoiding duplicates.
- **Error Handling & Logging:** Includes comprehensive logging and exception handling for better debugging and monitoring.

## Files Structure Overview:

- **instagram_scraper.py:** The main scraper script. It handles login, profile navigation, and data extraction.
insta_to_postgres.py:** Handles storing scraped Instagram data (captions and image URLs) into the PostgreSQL database. it also ensures that no duplicate posts are inserted by checking if the caption already exists in the database before performing the insertion.

- **tests - test_scraper.py:** contains unit tests for the InstagramScraper class, covering functionalities such as logging in, fetching post URLs, extracting captions, and scraping posts. The tests mock external dependencies like WebDriver and the database to isolate and verify the scraper's behavior. Run tests with python -m unittest test.py. 

- **config.py:** Contains Instagram and PostgreSQL credentials.

- **utils.py:** Sets up logging to output logs with a daily timestamp and the console, creating the log directory if it doesn't exist. Logs are captured at the INFO level with a specific format.

- **Dockerfile:** Used to build the Docker image for containerizing the scraper.

- **requirements.txt:** Lists all the Python dependencies needed to run the scraper.

# config.py
tokens = {
    'insta_username': 'your_instagram_username',
    'insta_password': 'your_instagram_password',
    'user': 'your_postgres_username',
    'password': 'your_postgres_password',
    'host': 'localhost',  # Change if using a remote DB
    'port': 5432  # Default PostgreSQL port
}

# PostgreSQL Database Schema
This project uses a PostgreSQL database to store scraped data. The schema includes a table called instagram_posts with the following columns:

   id: Auto-incremented primary key.
   caption: The caption of the Instagram post.
   image_url: The URL of the post's image.
   created_at: Timestamp when the record was created.

# Dockerfile Explanation

The Dockerfile defines how the Docker image is built:
Base Image: The scraper uses the python:3.8 base image to run the Python environment.
Working Directory: Sets the working directory to /app.
Copy Project Files: Copies all project files into the container.
Install Dependencies: Installs the required dependencies from requirements.txt.
Default Command: The default command is to run the instagram_scraper.py script.


## Customization

- **Target Profile:**
  Change the target Instagram profile by modifying the `navigate_to_profile` function in `instagram_scraper.py`.
  scraper.scrape_instagram(profile_url="https://www.instagram.com/target_profile/")


- **Post Limit:**
  Adjust the number of posts to scrape by updating the limit in the `scrape_instagram()` function:

  ```python
  for i, post_url in enumerate(post_urls[:5]):
  ```


License
This project is licensed under the MIT License. See the LICENSE file for more details.