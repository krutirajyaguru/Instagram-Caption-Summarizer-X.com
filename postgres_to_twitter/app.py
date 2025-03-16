import streamlit as st
import requests
import logging
from PIL import Image
from io import BytesIO
from summarizer import InstagramCaptionSummarizer
from utils import setup_logging

class StreamlitApp:
    """
    StreamlitApp class to create a Streamlit interface for summarizing Instagram captions
    and posting them to X.com (formerly Twitter).

    Attributes:
        summarizer (InstagramCaptionSummarizer): Instance to handle Instagram data and summaries.
    """

    def __init__(self):
        """Initializes the Streamlit app and sets up logging."""
        setup_logging()  # Initialize logging
        logging.info("Starting StreamlitApp")
        self.summarizer = InstagramCaptionSummarizer()

    def display_post(self):
        """
        Fetches and displays the latest Instagram post, including the caption and image.

        Returns:
            tuple: Instagram caption and image URL if available, otherwise (None, None).
        """
        try:
            # Retrieve the latest Instagram caption and image URL
            caption, image_url = self.summarizer.get_latest_post()
            st.markdown("### 📸 **Latest Instagram Post**")

            # Display the Instagram image if available
            if image_url:
                try:
                    response = requests.get(image_url)
                    img = Image.open(BytesIO(response.content))
                    img = img.resize((700, 500))
                    st.image(img, caption="Instagram Post", use_container_width=True)
                    logging.info("Image displayed successfully.")
                except Exception as e:
                    st.error(f"Error loading image: {e}")
                    logging.error(f"Error loading image: {e}")

            # Display the Instagram caption if available
            if caption:
                st.markdown(caption)
                logging.info("Caption displayed successfully.")
            else:
                st.warning("No Instagram caption available.")
                logging.warning("No Instagram caption available.")

            return caption, image_url
        except Exception as e:
            st.error("Error fetching Instagram post.")
            logging.error(f"Error fetching Instagram post: {e}")
            return None, None

    def run(self):
        """
        Main method to run the Streamlit app. Handles UI components and user interactions.
        """
        # Set up Streamlit page configuration
        st.set_page_config(page_title="Instagram Caption Summarizer")
        st.title("Instagram Caption Summarizer → X.com")

        # Display the latest Instagram post
        caption, image_url = self.display_post()

        # Ensure summarized_tweet is part of the session state for persistence
        if 'summarized_tweet' not in st.session_state:
            st.session_state.summarized_tweet = None

        # Add a separator for better UI organization
        st.markdown("---")
        st.markdown("### Summarize Caption")

        # Generate summary button and processing
        if st.button("Generate Summary", use_container_width=True):
            if caption:
                with st.spinner("Summarizing the caption..."):
                    try:
                        # Generate a summarized tweet from the Instagram caption
                        st.session_state.summarized_tweet = self.summarizer.summarize_caption(caption)
                        logging.info("Caption summarized successfully.")
                    except Exception as e:
                        logging.error(f"Error summarizing caption: {e}")

                # Display the summary if generated successfully
                if st.session_state.summarized_tweet:
                    st.success("Summary generated successfully!")
                    st.markdown(f"**Summarized Tweet:** \n\n{st.session_state.summarized_tweet}")
                else:
                    st.error("Failed to summarize caption.")
                    logging.error("Failed to summarize caption.")
            else:
                st.error("No caption available to summarize.")

        # Display tweet options if a summary exists
        if st.session_state.summarized_tweet:
            st.markdown("---")
            st.markdown("### Post Tweet")

            # Create columns for tweet options
            col1, col2 = st.columns(2)

            with col1:
                # Button to post tweet with image
                if st.button('📤 Tweet with Image', use_container_width=True):
                    try:
                        tweet_response = self.summarizer.post_tweet(st.session_state.summarized_tweet, image_url)
                        if tweet_response:
                            st.success("Tweet posted with an image successfully!")
                            st.json(tweet_response)
                            logging.info("Tweet posted with image successfully.")
                        else:
                            st.error("Failed to post tweet with an image.")
                            logging.error("Failed to post tweet with image.")
                    except Exception as e:
                        st.error("Error posting tweet with image.")
                        logging.error(f"Error posting tweet with image: {e}")

            with col2:
                # Button to post tweet without image
                if st.button('📄 Tweet without Image', use_container_width=True):
                    try:
                        tweet_response = self.summarizer.post_tweet(st.session_state.summarized_tweet, None)
                        if tweet_response:
                            st.success("Tweet posted without an image successfully!")
                            st.json(tweet_response)
                            logging.info("Tweet posted without image successfully.")
                        else:
                            st.error("Failed to post tweet without an image.")
                            logging.error("Failed to post tweet without image.")
                    except Exception as e:
                        st.error("Error posting tweet without image.")
                        logging.error(f"Error posting tweet without image: {e}")

if __name__ == "__main__":
    # Instantiate and run the Streamlit app
    app = StreamlitApp()
    app.run()
