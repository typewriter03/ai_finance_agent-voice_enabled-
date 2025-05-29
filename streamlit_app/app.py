import streamlit as st
import requests
import base64
from io import BytesIO

# --- Streamlit Settings ---
st.set_page_config(page_title="🎙️ Voice-Enabled Finance Assistant", layout="centered")
st.title("🤖 Voice-Enabled Finance Assistant")

# --- Config ---
VOICE_AGENT_URL = "http://localhost:8005"
ORCHESTRATOR_URL = "http://localhost:8006/orchestrate"

# --- Helper Functions ---
def process_query(query):
    """Process query through orchestrator and generate audio response"""
    # Step 1: Orchestrator
    st.subheader("📡 Fetching Market Summary")
    with st.spinner("Getting summary..."):
        try:
            orchestrator_resp = requests.post(ORCHESTRATOR_URL, json={"query": query})
            orchestrator_resp.raise_for_status()
            summary = orchestrator_resp.json().get("summary", "No summary available.")
            st.success("✅ Market summary received")
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

# --- Initialize session state ---
if 'recorded_audio' not in st.session_state:
    st.session_state.recorded_audio = None

# --- Layout: Two Columns ---
col1, col2 = st.columns(2)

# --- 🎤 Voice Input Section ---
with col1:
    st.header("🎤 Record Your Query")
    
    # Method 1: File Upload (Most reliable for Streamlit Cloud)
    st.markdown("**Upload an audio file:**")
    uploaded_audio = st.file_uploader(
        "Choose an audio file", 
        type=['wav', 'mp3', 'm4a', 'flac', 'ogg'],
        help="Record audio on your phone/computer and upload it here"
    )
    
    if uploaded_audio is not None:
        st.audio(uploaded_audio)
        
        if st.button("🔄 Process Uploaded Audio", key="process_upload"):
            # Step 1: Transcribe uploaded audio
            st.subheader("📝 Transcribing...")
            with st.spinner("Transcribing..."):
                try:
                    files = {'audio': (uploaded_audio.name, uploaded_audio, uploaded_audio.type)}
                    transcribe_resp = requests.post(f"{VOICE_AGENT_URL}/transcribe", files=files)
                    transcribe_resp.raise_for_status()
                    query = transcribe_resp.json().get("text", "").strip()
                except Exception as e:
                    st.error(f"❌ Transcription failed: {e}")
                    query = None
            
            if query:
                st.success("✅ Transcription successful")
                st.markdown(f"**Recognized Query:** `{query}`")
                process_query(query)
            else:
                st.warning("⚠️ No text recognized.")
    
    st.markdown("---")
    
    # Method 2: Browser Recording (Alternative - may not work on all deployments)
    st.markdown("**Or try browser recording:**")
    
    # Simple HTML5 audio recording
    audio_html = """
    <div style="border: 2px dashed #ccc; border-radius: 10px; padding: 20px; text-align: center; margin: 10px 0;">
        <p><strong>Browser Audio Recorder</strong></p>
        <button id="startRecord" onclick="startRecording()" style="margin: 5px; padding: 10px;">🎤 Start</button>
        <button id="stopRecord" onclick="stopRecording()" disabled style="margin: 5px; padding: 10px;">⏹️ Stop</button>
        <p id="recordStatus">Ready to record</p>
        <audio id="recordedAudio" controls style="display:none; width:100%; margin-top:10px;"></audio>
        <a id="downloadLink" style="display:none; margin-top:10px;">📥 Download Recording</a>
    </div>
    
    <script>
    let mediaRecorder;
    let recordedChunks = [];
    
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            recordedChunks = [];
            
            mediaRecorder.ondataavailable = function(event) {
                if (event.data.size > 0) {
                    recordedChunks.push(event.data);
                }
            };
            
            mediaRecorder.onstop = function() {
                const blob = new Blob(recordedChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(blob);
                
                const audioElement = document.getElementById('recordedAudio');
                audioElement.src = audioUrl;
                audioElement.style.display = 'block';
                
                const downloadLink = document.getElementById('downloadLink');
                downloadLink.href = audioUrl;
                downloadLink.download = 'recording.wav';
                downloadLink.style.display = 'block';
                downloadLink.textContent = '📥 Download Recording (Upload above)';
                
                // Stop all tracks
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
            };
            
            mediaRecorder.start();
            document.getElementById('startRecord').disabled = true;
            document.getElementById('stopRecord').disabled = false;
            document.getElementById('recordStatus').textContent = 'Recording... Click Stop when done';
            
        } catch (err) {
            document.getElementById('recordStatus').textContent = 'Error: Could not access microphone';
            console.error('Error:', err);
        }
    }
    
    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            document.getElementById('startRecord').disabled = false;
            document.getElementById('stopRecord').disabled = true;
            document.getElementById('recordStatus').textContent = 'Recording complete! Download and upload above.';
        }
    }
    </script>
    """
    
    st.components.v1.html(audio_html, height=250)
    
    st.info("💡 **Tip**: Browser recording creates a file you can download and then upload using the file uploader above.")

# --- ✍️ Text Input Section ---
with col2:
    st.header("✍️ Type Your Query")
    typed_query = st.text_area("💬 Ask your finance question:", placeholder="e.g. What's the outlook on Tesla stock?", height=100)
    
    if st.button("🚀 Submit Text Query", key="submit_text"):
        if typed_query.strip():
            process_query(typed_query.strip())
        else:
            st.warning("⚠️ Please enter a query.")

# --- Instructions ---
st.markdown("---")
st.markdown("### 📋 How to Use")
st.markdown("""
**Option 1 - File Upload (Recommended):**
1. Record audio on your phone/computer using any voice recorder app
2. Upload the audio file using the file uploader above
3. Click "Process Uploaded Audio"

**Option 2 - Browser Recording (Experimental):**
1. Click "Start" to begin browser recording
2. Speak your question
3. Click "Stop" to finish recording
4. Download the recorded file
5. Upload it using the file uploader above

**Option 3 - Text Input:**
- Simply type your question and click "Submit Text Query"

All methods provide both text summary and audio response.
""")