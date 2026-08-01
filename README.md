# ARIA — AI Voice Assistant
### Adaptive Research & Intelligent Assistant

A professional AI-powered voice assistant built with Python + Flask. Accepts voice or text queries, routes them intelligently between Wikipedia and Google Search, and responds with synthesised speech.

---

## 🏗️ Architecture

```
User Input (Voice / Text)
         │
         ▼
  ┌──────────────┐
  │  Flask Web   │  ←─ Browser UI (mic + text input)
  │   Server     │
  └──────┬───────┘
         │
         ▼
  Query Classifier
  (regex-based intent)
         │
    ┌────┴────┐
    ▼         ▼
Wikipedia  Google
  API      Search
    │         │
    └────┬────┘
         ▼
  Response Processing
         │
         ▼
  pyttsx3 TTS Engine
         │
         ▼
  Voice Output (WAV → browser)
```

---

## 📦 Installation

### 1. Clone / unzip the project
```bash
cd voice_assistant
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **pyaudio on Windows**: If `pip install pyaudio` fails, download the wheel from
> https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio and install with:
> `pip install PyAudio‑0.2.xx‑cpXX‑cpXX‑win_amd64.whl`

> **pyaudio on macOS**: `brew install portaudio && pip install pyaudio`

> **pyaudio on Linux**: `sudo apt-get install python3-pyaudio portaudio19-dev`

---

## 🚀 Running the App

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

---

## 🧰 Tech Stack

| Purpose | Library |
|---------|---------|
| Web framework | Flask |
| Speech-to-Text | SpeechRecognition + Google Web Speech API |
| Text-to-Speech | pyttsx3 (offline) |
| Wikipedia search | wikipedia |
| Google search | googlesearch-python + DuckDuckGo scraping |
| HTML scraping | BeautifulSoup4 |
| Audio recording | MediaRecorder API (browser) |

---

## 🎯 Features

- 🎙️ **Voice input** via browser microphone
- ⌨️ **Text input** fallback
- 🧠 **Smart routing** — Wikipedia for definitions, Google for news/how-to
- 🔊 **TTS voice output** — playable in browser
- 📊 **Waveform visualiser** during recording / playback
- 🕓 **Query history** pills for quick repeat
- ⚡ **Fast** — typically < 3 s for a full round-trip
- 🛡️ **Error handling** — graceful fallback on network failures

---

## 📡 API Endpoints

### `POST /api/query`
Process a text query.

**Request body:**
```json
{ "query": "What is Machine Learning?" }
```

**Response:**
```json
{
  "query": "What is Machine Learning?",
  "answer": "Machine learning is a branch of...",
  "source": "wikipedia",
  "title": "Machine learning",
  "url": "https://en.wikipedia.org/wiki/Machine_learning",
  "elapsed": 1.24,
  "audio_b64": "<base64-encoded WAV>"
}
```

---

### `POST /api/stt`
Convert uploaded audio file to text.

**Request:** `multipart/form-data` with field `audio` (WAV blob)

**Response:**
```json
{ "text": "What is artificial intelligence" }
```

---

## 🔧 Configuration

Edit these constants in `app.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `WIKI_TRIGGERS` | list of regex | Patterns that route to Wikipedia |
| `GOOGLE_TRIGGERS` | list of regex | Patterns that route to Google |
| `sentences=4` | 4 | Wikipedia summary sentence count |
| TTS `rate` | 165 | Speech rate (words/min) |
| TTS `volume` | 0.95 | Volume (0.0–1.0) |

---

## 🚀 Future Enhancements

- [ ] Wake-word detection ("Hey ARIA")
- [ ] OpenAI / Claude API integration
- [ ] Weather & News APIs
- [ ] Multi-language support
- [ ] Conversation memory / context
- [ ] Mobile PWA packaging
- [ ] Face-recognition login

---

## 🧪 Troubleshooting

| Issue | Fix |
|-------|-----|
| Mic not working | Allow microphone permissions in browser settings |
| `pyaudio` install fails | See platform notes above |
| No voice output | Check system speakers; pyttsx3 may need `espeak` on Linux |
| Slow Google results | DuckDuckGo scraping may be rate-limited; results degrade gracefully |
| Wikipedia DisambiguationError | Handled automatically by choosing the first suggestion |
