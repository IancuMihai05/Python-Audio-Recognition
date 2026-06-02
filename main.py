"""
Echipa: 31-E5
Studenti: IANCU MIHAI-ADRIAN, LĂZĂRESCU MOISE-ADRIAN
Tema proiect: D4-T1 | Achiziție semnal audio

Descriere:
Acest script realizează recunoașterea unei melodii captate prin microfon, comparând-o cu
o bază de date locală de fișiere audio. Extrage caracteristicile audio (MFCC - medie și deviație)
și calculează distanța cosinusoidală pentru a găsi cea mai bună potrivire.

Surse de inspirație și documentație:
- Librosa (MFCC): https://librosa.org/doc/main/generated/librosa.feature.mfcc.html
- PyAudio: https://people.csail.mit.edu/hubert/pyaudio/
- SciPy (Cosine): https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cosine.html
- Utilizare Inteligență Artificială
Model utilizat: Google Gemini
Rezumatul prompturilor tehnice folosite pentru generarea codului:
1. *"Cum folosesc librăria librosa pentru a extrage amprenta audio a unei piese? Generează codul pentru a calcula media și deviația standard a coeficienților MFCC și a-i uni într-un singur vector de caracteristici."*
2. *"Algoritmul confundă piesele din cauza distorsiunii de volum de la microfon. Cum ajustez matricea MFCC pentru a ignora amplitudinea generală și a păstra strict timbrul instrumentelor?"*
3. *"Care este cel mai eficient mod de a compara vectorul înregistrat live cu lista de vectori salvați în fișierul JSON? Oferă-mi codul pentru a calcula cea mai mică distanță cosinusoidală (cosine distance) între ei."*
"""

import os
import sys
import json
import wave
import pyaudio
import numpy as np
import librosa
from scipy.spatial.distance import cosine

JSON_DB_PATH = "semnaturi_audio.json"
FOLDER_MUZICA = "D:/Muzica"
DURATA_TEST = 15


def extrage_semnatura(file_path):
    # incarcam piesa la 22050 Hz si taiem linistea de la inceput
    audio_data, sr = librosa.load(file_path, sr=22050, duration=DURATA_TEST)
    audio_data, _ = librosa.effects.trim(audio_data, top_db=20)

    # 14 coeficienti, ignoram primul ca reprezinta doar volumul (C0)
    mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=14)
    mfccs = mfccs[1:, :]

    vector_medie = np.mean(mfccs.T, axis=0)
    vector_variatie = np.std(mfccs.T, axis=0)

    # combinam media si deviatia
    vector_final = np.concatenate((vector_medie, vector_variatie))
    return vector_final.tolist()


# CERINTA 2: Dezvoltati o functionalitate ce preia un folder cu fisiere audio si le defineste o semnatura
def preia_folder_si_defineste_semnaturi(folder_path):
    print(f"Scanez '{folder_path}'...")
    database = {}

    for fisier in os.listdir(folder_path):
        if fisier.endswith('.mp3') or fisier.endswith('.wav'):
            print(f"Procesez: {fisier}")
            cale_completa = os.path.join(folder_path, fisier)
            database[fisier] = extrage_semnatura(cale_completa)

    # salvam rezultatele in json
    with open(JSON_DB_PATH, 'w') as f:
        json.dump(database, f, indent=4)
    print("Baza de date a fost generata.")


# CERINTA 1: Dezvoltati o functionalitate ce capteaza semnal audio folosind un microfon
def captare_microfon(filename="output.wav", duration=DURATA_TEST):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = duration

    with wave.open(filename, 'wb') as wf:
        p = pyaudio.PyAudio()
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

        print(f'Recording {RECORD_SECONDS} seconds...')
        for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
            wf.writeframes(stream.read(CHUNK))
        print('Done')

        stream.close()
        p.terminate()


# CERINTA 3: Identificati semnalul audio captat cu una dintre semnaturile definite la punctul 2
def identifica_semnal(fisier_captat):
    print("Caut potrivirea...")
    with open(JSON_DB_PATH, 'r') as f:
        database = json.load(f)

    vector_captat = extrage_semnatura(fisier_captat)
    cea_mai_buna_potrivire = None
    distanta_minima = 999

    for nume, vec in database.items():
        dist = cosine(vector_captat, vec)
        if dist < distanta_minima:
            distanta_minima = dist
            cea_mai_buna_potrivire = nume

    print("-----------------------------------------")
    if distanta_minima < 0.10:
        print(f"Rezultat: {cea_mai_buna_potrivire} (scor: {distanta_minima:.4f})")
    else:
        print(f"N-am gasit exact. Cel mai aproape: {cea_mai_buna_potrivire} (scor: {distanta_minima:.4f})")
    print("-----------------------------------------")


if __name__ == "__main__":
    if not os.path.exists(JSON_DB_PATH):
        preia_folder_si_defineste_semnaturi(FOLDER_MUZICA)
    else:
        print("DB deja incarcat.")

    input("Apasa ENTER ca sa incepem inregistrarea...")
    captare_microfon("output.wav", DURATA_TEST)
    identifica_semnal("output.wav")