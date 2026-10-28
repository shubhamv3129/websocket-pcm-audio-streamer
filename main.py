"""
Main entry point for the Gemini Live application.
Starts the FastAPI application using uvicorn.
"""
import os
import uvicorn
from feature_websocket import app


def example_gemini_live_server() -> None:
    """
    Example function to run the Gemini Live FastAPI server.
    """
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting Gemini Live server on http://0.0.0.0:{port} ...")
    uvicorn.run(app, host="0.0.0.0", port=port)


def main() -> None:
    """
    Main function to execute the server.
    """
    example_gemini_live_server()


if __name__ == "__main__":
    main()
