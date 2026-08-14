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

# Answer through the hosted model or the extractive path, never a local one.
# Nothing serves Ollama in this image, so this saves a connection attempt per
# request — but it is set for quality rather than availability: a 4B model
# asked in Hindi who the Chief Justice is replies with a name out of its
# training data that appears nowhere in the corpus, and naming a sitting judge
# wrongly is worse than the few seconds it saves. scripts/check_fabrication.py
# is the check.
ENV NYAYSETU_DISABLE_OLLAMA=1

# Hugging Face Spaces routes traffic to port 7860 by default
EXPOSE 7860

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
