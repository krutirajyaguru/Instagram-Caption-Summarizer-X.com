import unittest
from unittest.mock import patch, MagicMock
from instagram_scraper import InstagramScraper

class TestInstagramScraper(unittest.TestCase):

    @patch('instagram_scraper.webdriver.Remote')
    def setUp(self, mock_webdriver):
        self.mock_driver = MagicMock()
        mock_webdriver.return_value = self.mock_driver

        self.scraper = InstagramScraper('test_user', 'test_pass')

    def test_setup_driver(self):
        self.assertIsNotNone(self.scraper.driver)
        self.scraper.driver.maximize_window.assert_called_once()

    @patch('instagram_scraper.WebDriverWait')
    def test_close_popup(self, mock_wait):
        mock_element = MagicMock()
        mock_wait.return_value.until.return_value = mock_element

        self.scraper.close_popup("//button[contains(text(), 'Not Now')]")
        mock_element.click.assert_called_once()

    @patch('instagram_scraper.WebDriverWait')
    def test_login(self, mock_wait):
        mock_wait.return_value.until = MagicMock()

        self.scraper.login()
        self.mock_driver.get.assert_called_with("https://www.instagram.com/accounts/login/")
        self.mock_driver.find_element.assert_any_call('name', 'username')
        self.mock_driver.find_element.assert_any_call('name', 'password')

    def test_navigate_to_profile(self):
        self.scraper.navigate_to_profile('https://www.instagram.com/testprofile/')
        self.mock_driver.get.assert_called_with('https://www.instagram.com/testprofile/')

    def test_fetch_post_urls(self):
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = 'https://www.instagram.com/p/testpost/'
        self.mock_driver.find_elements.return_value = [mock_element] * 3

        post_urls = self.scraper.fetch_post_urls()

        self.assertEqual(len(post_urls), 3)
        self.assertEqual(post_urls[0], 'https://www.instagram.com/p/testpost/')

    @patch('instagram_scraper.WebDriverWait')
    def test_extract_caption(self, mock_wait):
        mock_element = MagicMock()
        mock_element.text = "Test caption"
        mock_wait.return_value.until.return_value = mock_element

        caption = self.scraper.extract_caption()
        self.assertEqual(caption, "Test caption")

    @patch('instagram_scraper.WebDriverWait')
    def test_extract_image_url(self, mock_wait):
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = "https://image.url/test.jpg"
        mock_wait.return_value.until.return_value = mock_element

        image_url = self.scraper.extract_image_url()
        self.assertEqual(image_url, "https://image.url/test.jpg")

    @patch('instagram_scraper.PostgresDatabase')
    @patch('instagram_scraper.WebDriverWait')
    def test_scrape_posts(self, mock_wait, mock_db):
        self.scraper.fetch_post_urls = MagicMock(return_value=['https://www.instagram.com/p/testpost/'])
        self.scraper.extract_caption = MagicMock(return_value='Test Caption')
        self.scraper.extract_image_url = MagicMock(return_value='https://image.url/test.jpg')

        mock_db_instance = mock_db.return_value

        self.scraper.scrape_posts('https://www.instagram.com/testprofile/', limit=1)

        mock_db_instance.store_data_in_postgres.assert_called_once_with('Test Caption', 'https://image.url/test.jpg')
        self.mock_driver.quit.assert_called_once()

if __name__ == '__main__':
    unittest.main()