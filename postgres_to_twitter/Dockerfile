# Use an official Python image
FROM python:3.8

# Set the working directory
WORKDIR /app

# Copy the local project files to the container
COPY . /app/

# Set PYTHONPATH to recognize sibling folders
ENV PYTHONPATH="/app"

# Install dependencies
RUN pip install -r requirements.txt

# Expose the Streamlit port
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py"]


