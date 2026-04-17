# Audio Recognition System 🎵

This is a Python-based audio recognition tool that listens to audio via the microphone and identifies the song by matching it against a local directory of `.mp3` files.

## Features
1. **Microphone Recording:** Captures a 5-second audio sample from the default microphone.
2. **Local Database Generation:** Scans a specific folder for `.mp3` files and generates digital fingerprints using the Shazam API.
3. **Song Identification:** Compares the microphone recording against the local database and returns a match if the song exists in your folder.

## Technologies Used
* `PyAudio` & `wave` - For hardware microphone recording.
* `shazamio` - Asynchronous Shazam API wrapper for generating audio fingerprints and song identification.
* `asyncio` - For handling asynchronous API requests.
* `os` - For local file system scanning.

## How to use
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
