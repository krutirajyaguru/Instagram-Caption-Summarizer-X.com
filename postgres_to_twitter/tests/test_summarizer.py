import unittest
from unittest.mock import patch, MagicMock
from summarizer import InstagramCaptionSummarizer

class TestInstagramCaptionSummarizer(unittest.TestCase):

    def setUp(self):
        """Set up an instance of InstagramCaptionSummarizer for testing."""
        self.summarizer = InstagramCaptionSummarizer()
    
    # Mock the necessary components
    @patch('transformers.PegasusTokenizer.from_pretrained')
    @patch('transformers.AutoModelForSeq2SeqLM.from_pretrained')
    def test_summarize_caption(self, mock_tokenizer, mock_model):
        """Test summarizing an Instagram caption to tweet length."""
        
        caption = "This is a very long Instagram caption that will definitely be truncated because it exceeds the tweet length limit."
        
        # Assuming self.summarizer is already defined or mocked
        summarized_caption = self.summarizer.summarize_caption(caption)
        
        # Check if the result is a string and has the correct length
        self.assertIsInstance(summarized_caption, str)  # Ensure it's a string
        self.assertLessEqual(len(summarized_caption), 280)  # Tweet length limit (280 characters)

    def test_clean_incomplete_sentence(self):
        """Test trimming incomplete sentences from the summary."""
        text = "This is a complete sentence. This is incomplete"
        cleaned_text = self.summarizer.clean_incomplete_sentence(text)

        self.assertEqual(cleaned_text, "This is a complete sentence.")


if __name__ == '__main__':
    unittest.main()


