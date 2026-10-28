# 🎙️ Gemini Live — Real-Time Browser-to-FastAPI Audio Streaming

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-WebSockets-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![Web Audio API](https://img.shields.io/badge/Web_Audio-16kHz_PCM-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

A real-time browser audio recording and streaming application built with **FastAPI**, **WebSockets**, **Web Audio API**, and **Google Gemini (`gemini-2.5-flash`)**. It captures microphone audio in the browser, downsamples to 16kHz 16-bit mono PCM, converts to WAV in memory on the server, and streams Gemini transcriptions and answers back over the WebSocket.

---

## 📐 Architecture

```mermaid
sequenceDiagram
    participant Browser as Browser UI (index.html)
    participant WS as FastAPI WebSocket (/ws)
    participant WAV as In-Memory PCM-to-WAV
    participant Gemini as Google Gemini 2.5 Flash

    Browser->>WS: Connect & Send Handshake {"key": "..."}
    Browser->>Browser: Record Microphone & Decode to 16kHz PCM16
    Browser->>WS: Send Raw PCM16 Bytes
    WS->>WAV: pcm_to_wav_in_memory(16kHz, Mono, 16-bit)
    WAV->>Gemini: Upload Audio & generate_content_async(stream=True)
    loop Streaming Chunks
        Gemini-->>WS: Text Chunk
        WS-->>Browser: Stream Response Text
    end
    WS->>Gemini: delete_file() Cleanup
```

---

## 📁 Project Structure

```text
websocket-pcm-audio-streamer/
├── main.py                # Primary entry point starting Uvicorn on port 8000
├── feature_websocket.py   # FastAPI app, GET / index route, PCM-to-WAV helper, and /ws endpoint
├── index.html             # Browser client with MediaRecorder and 16kHz AudioContext decoder
├── .env.example           # Environment variable template
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `GEMINI_API_KEY` | Optional* | — | Server-side fallback Gemini API key (*can also be entered in the browser prompt) |
| `PORT` | No | `8000` | Port for the FastAPI Uvicorn server |

---

## 🚀 Quickstart

```bash
git clone https://github.com/shubhamv3129/websocket-pcm-audio-streamer.git
   cd websocket-pcm-audio-streamer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Optionally set GEMINI_API_KEY in .env

python3 main.py
```

Open `http://localhost:8000` in Chrome, click **Connect**, and click **Record** to stream audio to Gemini.
