# Use a slim Python image with a more recent Debian release (Bullseye) as the base
FROM python:3.11-slim-bullseye

# Install build dependencies for psycopg2 and other packages
# libpq-dev provides the pg_config executable and other PostgreSQL client libraries
# build-essential provides essential build tools like gcc, make, etc.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file and install dependencies
# This leverages Docker's layer caching, so if requirements.txt doesn't change,
# this step won't be re-run on subsequent builds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
# This includes the 'src' directory, which contains main.py, router, services, db, and backend.
# It also copies alembic and alembic.ini if they are in the root.
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini .
COPY static ./static

# Expose the port that Uvicorn will listen on
EXPOSE 8000

# Define the command to run Uvicorn
# The 'src.main:app' assumes your FastAPI app instance is named 'app'
# and is located in 'main.py' inside the 'src' directory.
# --host 0.0.0.0 makes the server accessible from outside the container.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
