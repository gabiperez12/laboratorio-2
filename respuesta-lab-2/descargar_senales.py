# descargar_senales.py
import os, urllib.request
import numpy as np
import librosa
import soundfile as sf

OUT = "senales"
os.makedirs(OUT, exist_ok=True)

TARGET_SR = 48000  # uniformizamos a 48 kHz
DUR = 12.0         # duración fija de cada referencia en segundos

# Función auxiliar: recorta, convierte a mono si corresponde, re-muestrea a 48 kHz
# y guarda la señal en formato WAV de 16 bits PCM.
def recortar_y_guardar(y, sr, nombre, mono=True):
    if mono and y.ndim > 1:
        y = librosa.to_mono(y)  # convertir a mono si la señal tiene más de un canal
    if sr != TARGET_SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=TARGET_SR)  # re-muestreo
        sr = TARGET_SR
    n = int(DUR * sr)  # número de muestras para 12 segundos
    if y.shape[-1] > n:
        y = y[..., :n]  # recorte a la duración deseada
    path = os.path.join(OUT, nombre)
    # guardado en WAV PCM 16 bits
    sf.write(path, y.T if y.ndim > 1 else y, sr, subtype="PCM_16")
    print(f" -> {path} sr={sr} dur={y.shape[-1]/sr:.2f}s ch={1 if y.ndim == 1 else y.shape[0]}")

# 1) Música tonal: fragmento de Tchaikovsky (ejemplo de señal armónica)
print("[1/3] Música tonal (nutcracker)")
y, sr = librosa.load(librosa.example("nutcracker"), sr=None, mono=False)
recortar_y_guardar(y, sr, "music_tonal.wav")

# 2) Voz: fragmento de LibriSpeech (ejemplo de señal de habla)
print("[2/3] Voz (libri1)")
y, sr = librosa.load(librosa.example("libri1"), sr=None, mono=False)
recortar_y_guardar(y, sr, "voz.wav")

# 3) Transitorios: fragmento con percusión (ejemplo de señal con transitorios)
print("[3/3] Transitorios (choice)")
y, sr = librosa.load(librosa.example("choice"), sr=None, mono=False)
recortar_y_guardar(y, sr, "transitorios.wav")
