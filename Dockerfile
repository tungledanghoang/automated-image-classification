# Using python slim version due to normal version taking a long time to pip install
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src ./src
COPY main.py ./

# Copy config files
COPY .env ./
COPY pytest.ini ./

# Copy testing code
COPY tests ./tests

# Run test
RUN pytest

# Run main code
CMD ["python", "main.py"]
