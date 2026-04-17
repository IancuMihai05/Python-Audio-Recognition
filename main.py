import wave
import pyaudio
import os
import asyncio
from shazamio import Shazam


def inregistare_microfon(durata=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = durata

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


async def amprenta(cale_folder=r"D:\Muzica"):
    rezultate = {}
    shazam = Shazam()

    for element in os.listdir(cale_folder):

        if element.endswith('.mp3'):
            cale = os.path.join(cale_folder, element)
            print(f"File: {element}")

            raspuns = await shazam.recognize(cale)

        if 'track' in raspuns:
            title = raspuns['track']['title']
            artist = raspuns['track']['subtitle']
            rezultate[element] = f'{artist} - {title}'
            print(f" Found: {artist} - {title}\n")
        else:
            print(f" Nu s-a putut genera amprenta\n")

    print("Baza de date melodii:")
    for fisier, melodie in rezultate.items():
        print(f"  {fisier} -> {melodie}")
    return rezultate


async def indentificator(baza_de_date):
    shazam = Shazam()

    raspuns_mic = await shazam.recognize("output.wav")

    if 'track' in raspuns_mic:
        title = raspuns_mic['track']['title']
        artist = raspuns_mic['track']['subtitle']
        amprenta_mic = f'{artist} - {title}'

        print(f"S-a auzit la microfon: {amprenta_mic}")
        if amprenta_mic in baza_de_date.values():
            print("Melodie gasita in folder")
        else:
            print("Melodie cunoscuta dar nu se afla in folder")
    else:
        print("Nu am putut recunoaste melodia")


if __name__ == "__main__":
    print("SISTEM DE RECUNOASTERE AUDIO")

    print("PASUL 1: Se scaneaza folderul cu muzica...\n")
    dictionar = asyncio.run(amprenta())

    print("\nPASUL 2: Inregistrare de la microfon...")
    input("Apasa tasta ENTER pentru a incepe inregistrarea...")
    inregistare_microfon()

    print("\n\nPASUL 3: Se identifica melodia...\n")
    asyncio.run(indentificator(dictionar))git init