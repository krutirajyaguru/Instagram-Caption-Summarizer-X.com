
# Use an official Python image
FROM python:3.8

# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Set PYTHONPATH to recognize sibling folders
ENV PYTHONPATH="/app"

# Install dependencies (if any)
RUN pip install -r requirements.txt

# Default command
CMD ["python3", "instagram_scraper.py"]

