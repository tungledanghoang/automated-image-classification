FROM python:3.11
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src ./src
COPY main.py ./

# Copy env settings
COPY .env ./

# Copy testing code
COPY tests ./tests

# Run test
RUN pytest

# Run main code
CMD ["python", "main.py"]
