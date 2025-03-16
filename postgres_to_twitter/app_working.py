import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from postgres_to_twitter.summarizer_working import InstagramCaptionSummarizer

class StreamlitApp:
    """
    A class to handle the Streamlit app interface and interaction with the InstagramCaptionSummarizer.
    
    Attributes:
        summarizer (InstagramCaptionSummarizer): Instance of the InstagramCaptionSummarizer class.
    """

    def __init__(self):
        """
        Initializes the Streamlit app by creating an instance of InstagramCaptionSummarizer.
        """
        self.summarizer = InstagramCaptionSummarizer()

    def display_post(self):
        """
        Fetches and displays the latest Instagram post, including the caption and image.

        Returns:
            tuple: A tuple containing the Instagram caption and image URL.
        """
        # Fetch Instagram caption and image
        caption, image_url = self.summarizer.get_latest_post()

        # Display post header
        st.markdown("### 📸 **Latest Instagram Post**")

        # Display Image (if available)
        if image_url:
            try:
                response = requests.get(image_url)
                img = Image.open(BytesIO(response.content))
                img = img.resize((700, 500))
                st.image(img, caption="Instagram Post", use_container_width=True)
            except Exception as e:
                st.error(f"Error loading image: {e}")

        # Display Caption (if available)
        if caption:
            st.markdown(caption)
        else:
            st.warning("No Instagram caption available.")

        return caption, image_url

    def run(self):
        """
        Runs the Streamlit app, including displaying posts and providing options for summarizing and posting to Twitter.
        """
        # Page Title and Intro
        st.set_page_config(page_title="Instagram Caption Summarizer")
        st.title("Instagram Caption Summarizer → X.com")

        # Display the Instagram post
        caption, image_url = self.display_post()

        # Store summarized_tweet for state management
        if 'summarized_tweet' not in st.session_state:
            st.session_state.summarized_tweet = None

        # Divider for better structure
        st.markdown("---")

        # Summarize Button Section
        st.markdown("### Summarize Caption")
        if st.button("Generate Summary", use_container_width=True):
            if caption:
                with st.spinner("Summarizing the caption..."):
                    st.session_state.summarized_tweet = self.summarizer.summarize_caption(caption)

                if st.session_state.summarized_tweet:
                    st.success("Summary generated successfully!")
                    st.markdown(f"**Summarized Tweet:** \n\n{st.session_state.summarized_tweet}")
                else:
                    st.error("Failed to summarize caption.")
            else:
                st.error("⚠️ No caption available to summarize.")

        # If summary exists, show Tweet options
        if st.session_state.summarized_tweet:
            st.markdown("---")
            st.markdown("### Post Tweet")

            # Tweet buttons with styled columns
            col1, col2 = st.columns(2)

            with col1:
                if st.button('📤 Tweet with Image', use_container_width=True):
                    tweet_response = self.summarizer.post_tweet(st.session_state.summarized_tweet, image_url)
                    if tweet_response:
                        st.success("Tweet posted with an image successfully!")
                        st.json(tweet_response)
                    else:
                        st.error("Failed to post tweet with an image.")

            with col2:
                if st.button('📄 Tweet without Image', use_container_width=True):
                    tweet_response = self.summarizer.post_tweet(st.session_state.summarized_tweet, None)
                    if tweet_response:
                        st.success("Tweet posted without an image successfully!")
                        st.json(tweet_response)
                    else:
                        st.error("Failed to post tweet without an image.")


if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
