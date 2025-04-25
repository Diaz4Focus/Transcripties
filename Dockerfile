FROM python:3.10-slim

WORKDIR /app

# Systeemvereisten + Java
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    openjdk-17-jre-headless \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data voor samenvatting
RUN python -c "import nltk; nltk.download('punkt')"

# Download LanguageTool voor NL spellingcontrole
RUN python -c "import language_tool_python; language_tool_python.LanguageTool('nl')"

# Download Whisper-model (medium — je kunt ook 'tiny', 'small' of 'large' kiezen)
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('medium')"

# Projectbestanden
COPY . .

CMD ["python", "app/main.py"]
