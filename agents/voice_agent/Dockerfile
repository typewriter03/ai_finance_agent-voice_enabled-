FROM python:3.10

WORKDIR /app

COPY . .

# Install FFmpeg (required for pydub)
RUN apt-get update && apt-get install -y ffmpeg

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8005

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
