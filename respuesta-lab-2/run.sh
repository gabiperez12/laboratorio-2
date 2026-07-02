#!/usr/bin/env bash
# run.sh — regenera todo el laboratorio con un solo comando (macOS / Linux)
# Requisito previo: ffmpeg instalado (brew install ffmpeg / sudo apt install ffmpeg)
set -e

# 1) entorno virtual
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

# 2) descargar y preparar las senales de referencia
python descargar_senales.py

# 3) codificar con AAC y Opus a 24/64/128 kbps y decodificar a WAV
python codificar.py

# 4) medir (bitrate real, LSD, STOI, PESQ) y generar espectrogramas diferenciales
python medir.py

# 5) generar las figuras del informe
python graficar.py

echo "Listo: resultados.csv, figuras/ y salidas/ regenerados."
