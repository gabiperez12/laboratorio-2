# medir.py
import os
import numpy as np
import librosa
import matplotlib.pyplot as plt
from pystoi import stoi
import librosa.display

IN_DIR = "senales"      # Carpeta con señales originales
OUT_DIR = "salida"      # Carpeta con señales codificadas y decodificadas
RESULTS = "resultados"  # Carpeta para guardar espectrogramas diferenciales
os.makedirs(RESULTS, exist_ok=True)

# Función para calcular el bitrate real de un archivo
# Nota: en los WAV decodificados siempre aparece ~768 kbps (PCM sin compresión).
def bitrate_real(path):
    size = os.path.getsize(path) * 8  # tamaño en bits
    dur = librosa.get_duration(path=path)  # duración en segundos
    return size / dur / 1000  # kbps

# Función para calcular LSD (Log-Spectral Distance)
# Compara espectrogramas logarítmicos de referencia y reconstruido.
def LSD(ref, rec, sr):
    S_ref = np.abs(librosa.stft(ref, n_fft=2048))**2
    S_rec = np.abs(librosa.stft(rec, n_fft=2048))**2
    log_ref = librosa.power_to_db(S_ref)
    log_rec = librosa.power_to_db(S_rec)

    # igualar número de columnas para evitar error de dimensiones
    min_cols = min(log_ref.shape[1], log_rec.shape[1])
    log_ref = log_ref[:, :min_cols]
    log_rec = log_rec[:, :min_cols]

    return np.mean(np.sqrt(np.mean((log_ref - log_rec)**2, axis=0)))

# Función para generar espectrograma diferencial y guardarlo como imagen PNG
def espectrograma_diff(ref, rec, sr, nombre):
    S_ref = np.abs(librosa.stft(ref, n_fft=2048))**2
    S_rec = np.abs(librosa.stft(rec, n_fft=2048))**2
    log_ref = librosa.power_to_db(S_ref)
    log_rec = librosa.power_to_db(S_rec)

    min_cols = min(log_ref.shape[1], log_rec.shape[1])
    diff = log_ref[:, :min_cols] - log_rec[:, :min_cols]

    plt.figure(figsize=(10,4))
    librosa.display.specshow(diff, sr=sr, x_axis="time", y_axis="hz", cmap="coolwarm")
    plt.colorbar(format="%+2.0f dB")
    plt.title(f"Diferencia espectrograma: {nombre}")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS, f"{nombre}_diff.png"))
    plt.close()

# Recorrer todos los archivos decodificados en carpeta 'salida/'
for f in os.listdir(OUT_DIR):
    if f.endswith(".wav"):
        nombre = os.path.splitext(f)[0]

        # Seleccionar la señal de referencia correcta según el nombre
        if "music_tonal" in nombre:
            ref_name = "music_tonal.wav"
        elif "voz" in nombre:
            ref_name = "voz.wav"
        elif "transitorios" in nombre:
            ref_name = "transitorios.wav"

        ref_path = os.path.join(IN_DIR, ref_name)
        rec_path = os.path.join(OUT_DIR, f)

        # Cargar señales original y reconstruida
        ref, sr = librosa.load(ref_path, sr=None, mono=True)
        rec, _ = librosa.load(rec_path, sr=sr, mono=True)

        # Igualar longitudes para evitar errores en métricas
        min_len = min(len(ref), len(rec))
        ref = ref[:min_len]
        rec = rec[:min_len]

        # Calcular métricas
        br = bitrate_real(rec_path)
        lsd = LSD(ref, rec, sr)
        print(f"{nombre}: bitrate={br:.1f} kbps, LSD={lsd:.2f}")

        # Generar espectrograma diferencial
        espectrograma_diff(ref, rec, sr, nombre)

        # Calcular STOI solo en señales de voz
        if "voz" in nombre:
            score = stoi(ref, rec, sr, extended=False)
            print(f" -> STOI={score:.3f}")
