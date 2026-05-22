import wave
import pyaudio
import os
import asyncio
from shazamio import Shazam

# Functia pentru a captura sunet de la microfon si a-l salva ca output.wav
def record_microphone(duration=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = duration

    with wave.open('output.wav', 'wb') as wf:
        p = pyaudio.PyAudio()
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))git status
        wf.setframerate(RATE)

        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

        print('Se inregistreaza...')
        for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
            wf.writeframes(stream.read(CHUNK))
            print(".", end='', flush=True)
        print('\nGata')

        stream.close()
        p.terminate()


# Functia pentru a scana folderul si a crea un dictionar cu amprentele melodiilor
async def generate_fingerprints(folder_path=r"D:\Music"):
    results = {}
    shazam = Shazam()

    for element in os.listdir(folder_path):
        # Proceseaza doar fisierele MP3
        if element.endswith('.mp3'):
            file_path = os.path.join(folder_path, element)
            print(f"Fisier: {element}")

            # Obtine informatii despre melodie de la Shazam API
            response = await shazam.recognize(file_path)

            if 'track' in response:
                title = response['track']['title']
                artist = response['track']['subtitle']
                results[element] = f'{artist} - {title}'
                print(f" Gasit: {artist} - {title}\n")
            else:
                print(f" Nu s-a putut genera amprenta\n")

    # Afiseaza baza de date finala cu melodiile locale
    print("Baza de date cu melodii:")
    for file, song in results.items():
        print(f"  {file} -> {song}")
    return results


# Functia pentru a identifica fisierul inregistrat si a-l compara cu baza de date
async def identify_audio(database):
    shazam = Shazam()

    # Recunoaste sunetul capturat de la microfon
    response_mic = await shazam.recognize("output.wav")

    if 'track' in response_mic:
        title = response_mic['track']['title']
        artist = response_mic['track']['subtitle']
        mic_fingerprint = f'{artist} - {title}'

        print(f"Detectie microfon: {mic_fingerprint}")

        # Verifica daca melodia exista in dictionarul creat la Pasul 1
        if mic_fingerprint in database.values():
            print("Melodia a fost gasita in folder")
        else:
            print("Melodia a fost recunoscuta, dar nu este in folder")
    else:
        print("Melodia nu a putut fi recunoscuta")


# Fluxul de executie
if __name__ == "__main__":
    print("SISTEM DE RECUNOASTERE AUDIO")

    # Pasul 1: Scaneaza fisierele locale si construieste baza de date cu amprente
    print("PASUL 1: Se scaneaza folderul de muzica...\n")
    song_database = asyncio.run(generate_fingerprints())

    # Pasul 2: Inregistreaza un nou sample audio de la microfon
    print("\nPASUL 2: Se inregistreaza de la microfon...")
    input("Apasa ENTER pentru a incepe inregistrarea...")
    record_microphone()

    # Pasul 3: Identifica sample-ul si cauta in baza de date locala
    print("\n\nPASUL 3: Se identifica melodia...\n")
    asyncio.run(identify_audio(song_database))