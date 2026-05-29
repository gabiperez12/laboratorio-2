# codificar.py
import subprocess
import os

IN_DIR = "senales"   # Carpeta con las señales originales descargadas
OUT_DIR = "salida"   # Carpeta donde se guardarán los archivos codificados y decodificados
os.makedirs(OUT_DIR, exist_ok=True)

bitrates = [24, 64, 128]  # Bitrates de prueba en kbps
senales = ["music_tonal.wav", "voz.wav", "transitorios.wav"]

# Este script recorre cada señal y la codifica en dos formatos: AAC y Opus.
# Para cada formato se generan tres versiones con diferentes bitrates (24, 64, 128 kbps).
# Luego, cada archivo comprimido se decodifica nuevamente a WAV para poder medir calidad.

for senal in senales:
    nombre = os.path.splitext(senal)[0]

    for br in bitrates:
        # Codificación AAC usando el encoder nativo de FFmpeg
        out_aac = os.path.join(OUT_DIR, f"{nombre}_aac_{br}.m4a")
        subprocess.run([
            "ffmpeg", "-y", "-i", os.path.join(IN_DIR, senal),
            "-c:a", "aac", "-b:a", f"{br}k", out_aac
        ], check=True)

        # Decodificación a WAV para análisis objetivo
        rec_aac = os.path.join(OUT_DIR, f"{nombre}_aac_{br}.wav")
        subprocess.run([
            "ffmpeg", "-y", "-i", out_aac, rec_aac
        ], check=True)

        # Codificación Opus usando libopus
        out_opus = os.path.join(OUT_DIR, f"{nombre}_opus_{br}.opus")
        subprocess.run([
            "ffmpeg", "-y", "-i", os.path.join(IN_DIR, senal),
            "-c:a", "libopus", "-b:a", f"{br}k", out_opus
        ], check=True)

        # Decodificación a WAV para análisis objetivo
        rec_opus = os.path.join(OUT_DIR, f"{nombre}_opus_{br}.wav")
        subprocess.run([
            "ffmpeg", "-y", "-i", out_opus, rec_opus
        ], check=True)

print("✅ Codificación completa. Archivos guardados en carpeta 'salida/'")
