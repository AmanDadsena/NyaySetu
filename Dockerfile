FROM python:3.10-slim

# Set up a new user named "user" with user ID 1000
# Hugging Face Spaces requires running as a non-root user
RUN useradd -m -u 1000 user
USER user

# Set home and path variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy requirements and install them
COPY --chown=user backend/requirements.txt $HOME/app/
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the rest of the backend code
COPY --chown=user backend $HOME/app/

# Hugging Face Spaces routes traffic to port 7860 by default
EXPOSE 7860

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
