"""
Echipa: 31-E5
Studenti: IANCU MIHAI-ADRIAN, LĂZĂRESCU MOISE-ADRIAN
Tema proiect: D4-T1 | Achiziție semnal audio
"""

import os
import json
import wave
import pyaudio
import numpy as np
import librosa
from scipy.spatial.distance import cosine

# Variabile globale
JSON_DB_PATH = "semnaturi_audio.json"
FOLDER_MUZICA = "D:/Muzica"
DURATA_TEST = 15  # Secunde (sincronizat perfect pentru JSON și Microfon)

def extrage_semnatura(file_path):
    """Extrage amprenta audio (fără volum general) dintr-un fișier."""
    # 1. Incarcam primele 15 secunde
    audio_data, sr = librosa.load(file_path, sr=22050, duration=DURATA_TEST)

    # 2. Tăiem liniștea de la început (dacă există) ca să nu ne strice media
    audio_data, _ = librosa.effects.trim(audio_data, top_db=20)

    # 3. Extragem 14 coeficienți MFCC
    mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=14)

    # 4. TRUCUL PRO: Aruncăm primul rând (indexul 0 reprezintă doar volumul)
    mfccs = mfccs[1:, :]

    # 5. Calculăm media și deviația standard pe cei 13 coeficienți rămași
    vector_medie = np.mean(mfccs.T, axis=0)
    vector_variatie = np.std(mfccs.T, axis=0)

    # 6. Unim rezultatele într-un super-vector de 26 de elemente
    vector_final = np.concatenate((vector_medie, vector_variatie))

    return vector_final.tolist()

def preia_folder_si_defineste_semnaturi(folder_path):
    """Cerința 2: Preia fisierele audio si le salveaza amprenta in JSON."""
    print(f"\n[1] Scanez folderul '{folder_path}'...")
    database = {}

    for fisier in os.listdir(folder_path):
        if fisier.endswith('.mp3') or fisier.endswith('.wav'):
            print(f"    Procesez: {fisier}...")
            cale_completa = os.path.join(folder_path, fisier)
            database[fisier] = extrage_semnatura(cale_completa)

    with open(JSON_DB_PATH, 'w') as f:
        json.dump(database, f, indent=4)
    print("    Gata! Semnaturile au fost salvate.")

def captare_microfon(filename="output.wav", duration=DURATA_TEST):
    """Cerința 1: Inregistreaza de la microfon folosind PyAudio."""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    with wave.open(filename, 'wb') as wf:
        p = pyaudio.PyAudio()
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

        print(f'\n[2] Se inregistreaza {duration} secunde', end='', flush=True)
        for _ in range(0, int(RATE / CHUNK * duration)):
            wf.writeframes(stream.read(CHUNK))
            print(".", end='', flush=True)
        print('\n    Gata\n')

        stream.close()
        p.terminate()

def identifica_semnal(fisier_captat):
    """Cerința 3: Compara inregistrarea cu baza de date."""
    print("[3] Caut potrivirea în baza de date...")

    with open(JSON_DB_PATH, 'r') as f:
        database = json.load(f)

    vector_captat = extrage_semnatura(fisier_captat)

    cea_mai_buna_potrivire = None
    distanta_minima = 999

    print("\n--- SCORURI CALCULATE ---")
    for nume_fisier, vector_baza in database.items():
        distanta = cosine(vector_captat, vector_baza)
        print(f" -> {nume_fisier}: {distanta:.4f}")

        if distanta < distanta_minima:
            distanta_minima = distanta
            cea_mai_buna_potrivire = nume_fisier

    print("-" * 50)
    # Prag de siguranță setat la 0.20
    if distanta_minima < 0.20:
        print(f" REZULTAT: Melodia este {cea_mai_buna_potrivire}")
    else:
        print(f" REZULTAT: Nu exista o potrivire exacta.")
        print(f" Cel mai mult seamana cu: {cea_mai_buna_potrivire}")
    print(f" (Distanta calculata: {distanta_minima:.4f})")
    print("-" * 50)

# --- Fluxul programului ---
if __name__ == "__main__":
    print("=== RECUNOASTERE AUDIO ===")

    if not os.path.exists(JSON_DB_PATH):
        preia_folder_si_defineste_semnaturi(FOLDER_MUZICA)
    else:
        print("[INFO] Baza de date a fost deja incarcata.")

    input(f"\nApasa ENTER pentru a inregistra {DURATA_TEST} secunde...")
    captare_microfon("output.wav", DURATA_TEST)
    identifica_semnal("output.wav")