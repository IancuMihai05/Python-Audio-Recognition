import wave
import pyaudio
import os
import asyncio
from shazamio import Shazam

    # Function to capture audio from the microphone and save it as output.wav


def record_microphone(duration=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = duration

    with wave.open('output.wav', 'wb') as wf:
        p = pyaudio.PyAudio()
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

        print('Recording...')
        for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
            wf.writeframes(stream.read(CHUNK))
            print(".", end='', flush=True)
        print('\nDone')

        stream.close()
        p.terminate()


# Function to scan the folder and create a dictionary of song fingerprints
async def generate_fingerprints(folder_path=r"D:\Music"):
    results = {}
    shazam = Shazam()

    for element in os.listdir(folder_path):
        # Only process MP3 files
        if element.endswith('.mp3'):
            file_path = os.path.join(folder_path, element)
            print(f"File: {element}")

            # Get song info from Shazam API
            response = await shazam.recognize(file_path)

            if 'track' in response:
                title = response['track']['title']
                artist = response['track']['subtitle']
                results[element] = f'{artist} - {title}'
                print(f" Found: {artist} - {title}\n")
            else:
                print(f" Could not generate fingerprint\n")

    # Display the final local song database
    print("Song database:")
    for file, song in results.items():
        print(f"  {file} -> {song}")
    return results


# Function to identify the recorded file and compare it with the database
async def identify_audio(database):
    shazam = Shazam()

    # Recognize the audio captured from the microphone
    response_mic = await shazam.recognize("output.wav")

    if 'track' in response_mic:
        title = response_mic['track']['title']
        artist = response_mic['track']['subtitle']
        mic_fingerprint = f'{artist} - {title}'

        print(f"Microphone detection: {mic_fingerprint}")

        # Check if the song exists in the dictionary created in Step 1
        if mic_fingerprint in database.values():
            print("Song found in folder")
        else:
            print("Song recognized but not in folder")
    else:
        print("Could not recognize song")


# Execution flow
if __name__ == "__main__":
    print("AUDIO RECOGNITION SYSTEM")

    # Step 1: Scan local files and build fingerprint database
    print("STEP 1: Scanning music folder...\n")
    song_database = asyncio.run(generate_fingerprints())

    # Step 2: Record new audio sample from microphone
    print("\nSTEP 2: Recording from microphone...")
    input("Press ENTER to start recording...")
    record_microphone()

    # Step 3: Identify the sample and search in local database
    print("\n\nSTEP 3: Identifying song...\n")
    asyncio.run(identify_audio(song_database))
