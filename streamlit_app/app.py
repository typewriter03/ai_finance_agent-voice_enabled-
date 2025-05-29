import streamlit as st
import sounddevice as sd
from scipy.io.wavfile import write
import requests
import io

# --- Streamlit Settings ---
st.set_page_config(page_title="🎙️ Voice-Enabled Finance Assistant", layout="centered")
st.title("🤖 Voice-Enabled Finance Assistant")

# --- Config ---
VOICE_AGENT_URL = "http://localhost:8005"
ORCHESTRATOR_URL = "http://localhost:8006/orchestrate"

# --- Layout: Two Columns ---
col1, col2 = st.columns(2)

# --- 🎤 Voice Input Section ---
with col1:
    st.header("🎤 Speak Your Query")
    duration = st.slider("⏱️ Duration (seconds)", 1, 20, 10, key="duration_slider")
    if st.button("🔴 Start Recording"):
        fs = 16000
        st.info("Recording...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        st.success("✅ Recording complete!")

        # Save as WAV
        wav_io = io.BytesIO()
        write(wav_io, fs, recording)
        wav_io.seek(0)

        # Step 1: Transcribe
        st.subheader("📝 Transcribing...")
        with st.spinner("Transcribing..."):
            try:
                files = {'audio': ('recording.wav', wav_io, 'audio/wav')}
                transcribe_resp = requests.post(f"{VOICE_AGENT_URL}/transcribe", files=files)
                transcribe_resp.raise_for_status()
                query = transcribe_resp.json().get("text", "").strip()
            except Exception as e:
                st.error(f"❌ Transcription failed: {e}")
                query = None

        if query:
            st.success("✅ Transcription successful")
            st.markdown(f"**Recognized Query:** `{query}`")

            # Step 2: Orchestrator
            st.subheader("📡 Fetching Market Summary")
            with st.spinner("Getting summary..."):
                try:
                    orchestrator_resp = requests.post(ORCHESTRATOR_URL, json={"query": query})
                    orchestrator_resp.raise_for_status()
                    summary = orchestrator_resp.json().get("summary", "No summary available.")
                    st.success("✅ Market summary received, Please Scroll Down")
                    st.markdown("### 📈 Summary")
                    st.markdown(f"> {summary}")
                except Exception as e:
                    st.error(f"❌ Orchestrator error: {e}")
                    summary = None

            # Step 3: Generate Audio
            if summary:
                st.subheader("🔊 Audio Response")
                with st.spinner("Generating audio..."):
                    try:
                        speak_resp = requests.post(f"{VOICE_AGENT_URL}/speak", json={"text": summary})
                        speak_resp.raise_for_status()
                        st.audio(speak_resp.content, format="audio/mp3")
                    except Exception as e:
                        st.warning(f"⚠️ Audio generation failed: {e}")
        else:
            st.warning("⚠️ No text recognized.")

# --- ✍️ Text Input Section ---
with col2:
    st.header("✍️ Type Your Query")
    typed_query = st.text_area("💬 Ask your finance question:", placeholder="e.g. What's the outlook on Tesla stock?")
    if st.button("🚀 Submit Text Query"):
        if typed_query.strip():
            query = typed_query.strip()

            # Step 1: Orchestrator
            st.subheader("📡 Fetching Market Summary")
            with st.spinner("Getting summary..."):
                try:
                    orchestrator_resp = requests.post(ORCHESTRATOR_URL, json={"query": query})
                    orchestrator_resp.raise_for_status()
                    summary = orchestrator_resp.json().get("summary", "No summary available.")
                    st.success("✅ Market summary received, Please Scroll Down")
                    st.markdown("### 📈 Summary")
                    st.markdown(f"> {summary}")
                except Exception as e:
                    st.error(f"❌ Orchestrator error: {e}")
                    summary = None

            # Step 2: Generate Audio
            if summary:
                st.subheader("🔊 Audio Response")
                with st.spinner("Generating audio..."):
                    try:
                        speak_resp = requests.post(f"{VOICE_AGENT_URL}/speak", json={"text": summary})
                        speak_resp.raise_for_status()
                        st.audio(speak_resp.content, format="audio/mp3")
                    except Exception as e:
                        st.warning(f"⚠️ Audio generation failed: {e}")
        else:
            st.warning("⚠️ Please enter a query.")

