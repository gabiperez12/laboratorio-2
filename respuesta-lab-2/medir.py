# medir.py
import os
import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pystoi import stoi
from pesq import pesq
from scipy.signal import correlate
import librosa.display
import csv

# Nota sobre ViSQOL: pip install visqol falla en Windows y en varios entornos
# (no hay rueda pre-compilada). Siguiendo la consigna (seccion 2.0 y 2.3),
# usamos las metricas de respaldo: LSD (todas las senales), STOI y PESQ (voz).
# Esto queda declarado tambien en el informe.

# preparar archivo CSV
csv_path = "resultados.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["senal", "codec", "bitrate", "br_real", "LSD", "STOI", "PESQ"])

IN_DIR = "senales"                       # Carpeta con senales originales
COD_DIR = os.path.join("salidas", "codificadas")    # Archivos comprimidos (.m4a / .opus)
DEC_DIR = os.path.join("salidas", "decodificadas")  # WAV decodificados para medir
FIG_DIR = "figuras"                      # Carpeta para los espectrogramas diferenciales
os.makedirs(FIG_DIR, exist_ok=True)

def bitrate_real(path_codificado):
    # Bitrate efectivo = tamano del archivo comprimido / duracion de la senal
    size = os.path.getsize(path_codificado) * 8
    dur = librosa.get_duration(path=path_codificado)
    return size / dur / 1000  # kbps

def alinear(ref, rec):
    # Los codecs introducen retardo (AAC ~2048 muestras, Opus ~312-960).
    # Buscamos el lag por correlacion cruzada y compensamos antes de comparar.
    n = min(len(ref), len(rec))
    corr = correlate(rec[:n], ref[:n], mode="full")
    lag = np.argmax(corr) - (n - 1)
    if lag > 0:
        rec = rec[lag:]
    elif lag < 0:
        ref = ref[-lag:]
    n = min(len(ref), len(rec))
    return ref[:n], rec[:n], lag

def LSD(ref, rec, sr):
    S_ref = np.abs(librosa.stft(ref, n_fft=2048))**2
    S_rec = np.abs(librosa.stft(rec, n_fft=2048))**2
    log_ref = librosa.power_to_db(S_ref)
    log_rec = librosa.power_to_db(S_rec)
    min_cols = min(log_ref.shape[1], log_rec.shape[1])
    log_ref = log_ref[:, :min_cols]
    log_rec = log_rec[:, :min_cols]
    return np.mean(np.sqrt(np.mean((log_ref - log_rec)**2, axis=0)))

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
    plt.savefig(os.path.join(FIG_DIR, f"{nombre}_diff.png"))
    plt.close()

# recorrer todos los archivos decodificados
for f in sorted(os.listdir(DEC_DIR)):
    if f.endswith(".wav"):
        nombre = os.path.splitext(f)[0]

        if "music_tonal" in nombre:
            ref_name = "music_tonal.wav"
        elif "voz" in nombre:
            ref_name = "voz.wav"
        elif "transitorios" in nombre:
            ref_name = "transitorios.wav"

        ref_path = os.path.join(IN_DIR, ref_name)
        rec_path = os.path.join(DEC_DIR, f)

        ref, sr = librosa.load(ref_path, sr=None, mono=True)
        rec, _ = librosa.load(rec_path, sr=sr, mono=True)

        # alineacion temporal antes de medir (consigna 2.3)
        ref_a, rec_a, lag = alinear(ref, rec)

        # codec y bitrate nominal desde el nombre del archivo
        if "aac" in nombre:
            codec = "AAC"
            ext = ".m4a"
        elif "opus" in nombre:
            codec = "Opus"
            ext = ".opus"
        else:
            codec = "?"
            ext = ""

        try:
            br_nominal = int(nombre.split("_")[-1])
        except:
            br_nominal = 0

        # bitrate real medido sobre el archivo comprimido (no el WAV)
        cod_path = os.path.join(COD_DIR, nombre + ext)
        br = bitrate_real(cod_path) if os.path.exists(cod_path) else ""

        lsd = LSD(ref_a, rec_a, sr)
        print(f"{nombre}: lag={lag}, bitrate real={br:.1f} kbps, LSD={lsd:.2f}")

        espectrograma_diff(ref_a, rec_a, sr, nombre)

        # STOI y PESQ solo para voz
        if "voz" in nombre:
            score_stoi = stoi(ref_a, rec_a, sr, extended=False)
            # PESQ trabaja a 16 kHz (modo wide-band): re-muestreamos
            ref16 = librosa.resample(ref_a, orig_sr=sr, target_sr=16000)
            rec16 = librosa.resample(rec_a, orig_sr=sr, target_sr=16000)
            score_pesq = pesq(16000, ref16, rec16, "wb")
            print(f" -> STOI={score_stoi:.3f}, PESQ={score_pesq:.3f}")
        else:
            score_stoi = ""
            score_pesq = ""

        # escribir fila en CSV
        with open(csv_path, "a", newline="") as f_out:
            writer = csv.writer(f_out)
            writer.writerow([ref_name.replace(".wav",""), codec, br_nominal,
                             round(br, 1) if br != "" else "",
                             lsd, score_stoi, score_pesq])

print("Medicion completa. Resultados en resultados.csv y figuras en 'figuras/'")
