"""
Feature module for the Gemini Live WebSocket logic.
Handles PCM to WAV conversion and streaming communication with the Gemini model.
"""
import io
import os
from pathlib import Path
import wave

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from google import generativeai as genai

load_dotenv()

app = FastAPI(title="Gemini Streaming Audio Demo")


@app.get("/")
async def serve_index() -> FileResponse:
    """Serves the frontend HTML interface."""
    index_path = Path(__file__).resolve().parent / "index.html"
    return FileResponse(index_path)


def pcm_to_wav_in_memory(
    pcm_data: bytes, channels: int, sample_width: int, frame_rate: int
) -> bytes:
    """
    Converts raw PCM data to a WAV file format in memory.

    Args:
        pcm_data (bytes): The raw PCM audio data.
        channels (int): Number of audio channels.
        sample_width (int): Sample width in bytes.
        frame_rate (int): Sampling rate in Hz.

    Returns:
        bytes: The formatted WAV file data.
    """
    mem_file = io.BytesIO()
    with wave.open(mem_file, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(frame_rate)
        wf.writeframes(pcm_data)
    mem_file.seek(0)
    return mem_file.read()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for receiving audio and streaming Gemini model responses.

    Args:
        websocket (WebSocket): The WebSocket connection instance.
    """
    await websocket.accept()
    print("WebSocket connection accepted. Waiting for API key or initial handshake.")

    try:
        initial_message = await websocket.receive_json()
        api_key = initial_message.get("key") or os.getenv("GEMINI_API_KEY")

        if not api_key:
            await websocket.close(code=1008, reason="API key not provided.")
            return

        # Configure the Generative AI library with the provided key
        genai.configure(api_key=api_key)
        print("API Key configured for the session.")

        model = genai.GenerativeModel("models/gemini-2.5-flash")

        while True:
            pcm_data = await websocket.receive_bytes()
            print(f"Received {len(pcm_data)} bytes of audio data.")

            wav_data = pcm_to_wav_in_memory(
                pcm_data, channels=1, sample_width=2, frame_rate=16000
            )

            print("Uploading audio file...")
            audio_file = genai.upload_file(io.BytesIO(wav_data), mime_type="audio/wav")
            print("File uploaded successfully.")

            prompt = (
                "Listen to this audio and provide a transcript. "
                "If there's background noise, describe it. If it's a question, answer it."
            )
            response = await model.generate_content_async(
                [prompt, audio_file], stream=True
            )

            async for chunk in response:
                if chunk.text:
                    await websocket.send_text(chunk.text)

            genai.delete_file(audio_file.name)
            print("Uploaded file cleaned up.")

    except Exception as exc:
        print(f"An error occurred: {exc}")
    finally:
        print("WebSocket connection closed.")
