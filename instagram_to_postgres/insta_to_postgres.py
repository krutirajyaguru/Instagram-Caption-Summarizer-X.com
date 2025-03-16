import psycopg2
import logging
from config import tokens
from utils import setup_logging

DB_CONFIG = {
    "dbname": 'insta_posts_db',
    "user": tokens['user'],
    "password": tokens['password'],
    "host": tokens['host'],
    "port": tokens['port']
}

class PostgresDatabase:
    def __init__(self):
        self.db_config = DB_CONFIG
        self.connection = None
        self.cursor = None
        self.logger = logging.getLogger(__name__)
        self.connect()
        self.create_table_if_not_exists()

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor()
            self.logger.info("Connected to PostgreSQL database.")
        except Exception as e:
            self.logger.error(f"Error connecting to PostgreSQL: {e}")
            raise

    def create_table_if_not_exists(self):
        try:
            query = """
            CREATE TABLE IF NOT EXISTS instagram_posts (
                id SERIAL PRIMARY KEY,
                caption TEXT UNIQUE,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            self.cursor.execute(query)
            self.connection.commit()
            self.logger.info("Ensured 'instagram_posts' table exists.")
        except Exception as e:
            self.logger.error(f"Error creating table: {e}")
            raise

    def check_if_caption_exists(self, caption):
        try:
            self.cursor.execute("SELECT id FROM instagram_posts WHERE caption = %s", (caption,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Error checking caption existence: {e}")
            raise

    def insert_post_data(self, caption, image_url):
        try:
            if self.check_if_caption_exists(caption):
                self.logger.info("Caption already exists. Skipping insertion.")
                return

            query = """
            INSERT INTO instagram_posts (caption, image_url)
            VALUES (%s, %s);
            """
            self.cursor.execute(query, (caption, image_url))
            self.connection.commit()
            self.logger.info("Successfully stored post in PostgreSQL.")
        except Exception as e:
            self.logger.error(f"Error inserting post data: {e}")
            raise

    def store_data_in_postgres(self, caption, image_url):
        try:
            self.insert_post_data(caption, image_url)
        except Exception as e:
            self.logger.error(f"Error during storing data: {e}")

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            self.logger.info("Closed PostgreSQL connection.")
        except Exception as e:
            self.logger.error(f"Error closing connection: {e}")


def main():
    setup_logging()
    db = PostgresDatabase()

    sample_caption = "Sample Instagram Post"
    sample_image_url = "https://example.com/sample.jpg"

    db.store_data_in_postgres(sample_caption, sample_image_url)
    db.close()

if __name__ == "__main__":
    main()

