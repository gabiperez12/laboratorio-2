# run.ps1 — regenera todo el laboratorio con un solo comando (Windows 10/11)
# Requisito previo: ffmpeg instalado (winget install Gyan.FFmpeg) y en el PATH.
# Si la activacion del venv falla, ejecutar antes:
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

$ErrorActionPreference = "Stop"

# 1) entorno virtual
if (-not (Test-Path ".venv")) {
    py -3.10 -m venv .venv
}
.\.venv\Scripts\Activate.ps1
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

Write-Host "Listo: resultados.csv, figuras/ y salidas/ regenerados."
