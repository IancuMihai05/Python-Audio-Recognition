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
- Asistent AI (ajutor la depanare, structurare algoritmi DSP și explicații)
"""

import os
import json
import wave
import pyaudio
import numpy as np
import librosa
from scipy.spatial.distance import cosine

# Setări generale pentru a sincroniza perfect microfonul cu baza de date
JSON_DB_PATH = "semnaturi_audio.json"
FOLDER_MUZICA = "D:/Muzica"
DURATA_TEST = 15  # Secunde

def extrage_semnatura(file_path):
    """Extrage o amprentă audio din primele 15 secunde ale unui fișier."""

    # 1. Încărcăm fișierul audio (convertit automat la mono, 22050 Hz)
    audio_data, sr = librosa.load(file_path, sr=22050, duration=DURATA_TEST)

    # 2. Eliminăm automat liniștea de la începutul fișierului, dacă există
    audio_data, _ = librosa.effects.trim(audio_data, top_db=20)

    # 3. Extragem 14 coeficienți MFCC (care descriu forma și timbrul sunetului)
    mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=14)

    # 4. Eliminăm primul coeficient (index 0) deoarece reprezintă doar volumul, nu și calitatea sunetului
    mfccs = mfccs[1:, :]

    # 5. Calculăm media (timbrul general) și deviația standard (variația/ritmul)
    vector_medie = np.mean(mfccs.T, axis=0)
    vector_variatie = np.std(mfccs.T, axis=0)

    # 6. Combinăm cele două rezultate într-un vector final de 26 de elemente
    vector_final = np.concatenate((vector_medie, vector_variatie))

    return vector_final.tolist()

def preia_folder_si_defineste_semnaturi(folder_path):
    """Cerința 2: Scanează folderul cu muzică și salvează amprentele în fișierul JSON."""
    print(f"\n[1] Scanez folderul '{folder_path}'...")
    database = {}

    # Căutăm doar fișierele mp3 și wav
    for fisier in os.listdir(folder_path):
        if fisier.endswith('.mp3') or fisier.endswith('.wav'):
            print(f"    Procesez: {fisier}...")
            cale_completa = os.path.join(folder_path, fisier)

            # Salvăm amprenta calculată în dicționar
            database[fisier] = extrage_semnatura(cale_completa)

    # Salvăm dicționarul în format JSON pentru a nu repeta procesul la fiecare rulare
    with open(JSON_DB_PATH, 'w') as f:
        json.dump(database, f, indent=4)
    print("    Gata! Semnaturile au fost salvate.")

def captare_microfon(filename="output.wav", duration=DURATA_TEST):
    """Cerința 1: Captează semnalul de la microfon și îl salvează într-un fișier temporar WAV."""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1 # Canal mono pentru compatibilitate cu Librosa
    RATE = 44100 # Rata de eșantionare standard pentru microfon

    with wave.open(filename, 'wb') as wf:
        p = pyaudio.PyAudio()
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        # Deschidem conexiunea cu microfonul fizic
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

        print(f'\n[2] Se inregistreaza {duration} secunde', end='', flush=True)

        # Citim datele audio în bucăți (chunks) și le scriem în fișier
        for _ in range(0, int(RATE / CHUNK * duration)):
            wf.writeframes(stream.read(CHUNK))
            print(".", end='', flush=True)
        print('\n    Gata\n')

        # Oprim fluxul de date și eliberăm resursele sistemului
        stream.close()
        p.terminate()

def identifica_semnal(fisier_captat):
    """Cerința 3: Compară semnalul înregistrat cu vectorii din baza de date."""
    print("[3] Caut potrivirea în baza de date...")

    # Încărcăm amprentele deja salvate
    with open(JSON_DB_PATH, 'r') as f:
        database = json.load(f)

    # Calculăm amprenta matematică pentru fișierul audio abia înregistrat
    vector_captat = extrage_semnatura(fisier_captat)

    cea_mai_buna_potrivire = None
    distanta_minima = 999  # Inițializăm cu o valoare exagerat de mare pentru a putea fi suprascrisă

    # Căutăm melodia cu cea mai mică distanță cosinusoidală față de înregistrarea noastră
    for nume_fisier, vector_baza in database.items():
        distanta = cosine(vector_captat, vector_baza)

        if distanta < distanta_minima:
            distanta_minima = distanta
            cea_mai_buna_potrivire = nume_fisier

    # Afișăm rezultatul final curat
    print("-" * 50)
    # 0.20 este un prag de toleranță (dacă scorul este mai mare de atât, înseamnă că nu a recunoscut piesa clar)
    if distanta_minima < 0.20:
        print(f" REZULTAT: Melodia este {cea_mai_buna_potrivire}")
    else:
        print(f" REZULTAT: Nu exista o potrivire exacta.")
        print(f" Cel mai mult seamana cu: {cea_mai_buna_potrivire}")
    print(f" (Distanta calculata: {distanta_minima:.4f})")
    print("-" * 50)

# --- Execuția principală a programului ---
if __name__ == "__main__":
    print("=== RECUNOASTERE AUDIO ===")

    # Verificăm dacă avem deja baza de date generată; dacă nu, o creăm (Cerința 2)
    if not os.path.exists(JSON_DB_PATH):
        preia_folder_si_defineste_semnaturi(FOLDER_MUZICA)
    else:
        print("[INFO] Baza de date a fost deja incarcata din fisier.")

    # Așteptăm confirmarea utilizatorului pentru a porni înregistrarea (Cerința 1)
    input(f"\nApasa ENTER pentru a inregistra {DURATA_TEST} secunde...")
    captare_microfon("output.wav", DURATA_TEST)

    # Lansăm procesul de recunoaștere (Cerința 3)
    identifica_semnal("output.wav")