from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import whisper
from gtts import gTTS
import os
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import requests

app = FastAPI(title="Voice Agent")

# Load Whisper model
model = whisper.load_model("base")


@app.get("/")
def root():
    return {"message": "Voice Agent is running"}


# Transcribe Endpoint (for Streamlit)
@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    # Save uploaded audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
        tmp_audio.write(await audio.read())
        tmp_audio_path = tmp_audio.name

    # Transcribe using Whisper
    result = model.transcribe(tmp_audio_path)
    query_text = result["text"]
    print("📝 Transcribed Text:", query_text)

    return {"text": query_text}


# Speak Endpoint (text to speech + audio response)
@app.post("/speak")
async def speak(data: dict):
    text = data.get("text", "")
    if not text:
        return {"error": "No text provided."}

    tts = gTTS(text)
    output_path = os.path.join(tempfile.gettempdir(), "response.mp3")
    tts.save(output_path)

    return FileResponse(output_path, media_type="audio/mpeg", filename="response.mp3")


# Legacy full pipeline if needed
@app.post("/voice-query/")
async def voice_query(audio: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
        tmp_audio.write(await audio.read())
        tmp_audio_path = tmp_audio.name

    result = model.transcribe(tmp_audio_path)
    query_text = result["text"]
    print("📝 Transcribed Text:", query_text)

    # 🔁 Call your orchestrator endpoint instead of hardcoded summarizer
    response = requests.post(
        "http://localhost:8006/orchestrate",
        json={"query": query_text}
    )

    response_json = response.json()
    final_text = response_json.get("summary", "No response")

    tts = gTTS(final_text)
    output_path = os.path.join(tempfile.gettempdir(), "response.mp3")
    tts.save(output_path)

    # Speed up the audio file by 1.5x
    audio = AudioSegment.from_file(output_path)
    speeded_up_audio = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * 1.5)
    })
    speeded_up_audio = speeded_up_audio.set_frame_rate(audio.frame_rate)
    speeded_up_audio.export(output_path, format="mp3")

    return {
        "text": query_text,
        "summary": final_text,
        "audio_url": f"http://localhost:8005/speak?text={final_text.replace(' ', '+')}"
    }
