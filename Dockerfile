FROM python:3.12-slim

# Prevent Python from writing .pyc files & force stdout/stderr to stay unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y vim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt


# Copy project files
COPY . /app/

# Create instance folder and empty app.log
RUN mkdir -p /app/instance && touch /app/instance/app.log

# Expose port 80
EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--ws=websockets", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info", "--workers", "1"]
