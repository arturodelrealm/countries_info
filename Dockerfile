FROM python:3.12

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install jupyter

# Copy the application code
COPY .. .

# Expose the Streamlit default port
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]