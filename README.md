# laboratorio-2

Repositorio correspondiente al Laboratorio 2 de la asignatura Compresión y Codificación:
análisis comparativo de códecs de audio (AAC-LC vs. Opus) a 24, 64 y 128 kbps sobre
tres señales de referencia (música tonal, voz y transitorios).

## Cómo reproducir todo

Requisito previo: `ffmpeg` instalado y en el PATH.

```bash
# macOS / Linux
cd respuesta-lab-2
./run.sh
```

```powershell
# Windows 10/11
cd respuesta-lab-2
.\run.ps1
```

Un solo comando regenera señales, archivos codificados/decodificados,
`resultados.csv` y todas las figuras.

## Estructura

```
respuesta-lab-2/
├── run.sh / run.ps1        ← pipeline completo en un comando
├── requirements.txt
├── descargar_senales.py    ← descarga y prepara las 3 referencias (48 kHz, 12 s)
├── codificar.py            ← AAC-LC y Opus a 24/64/128 kbps vía ffmpeg
├── medir.py                ← bitrate real, LSD, STOI, PESQ + espectrogramas diferenciales
├── graficar.py             ← figuras del informe a partir de resultados.csv
├── senales/                ← referencias WAV (ground truth)
├── salidas/
│   ├── codificadas/        ← .m4a / .opus
│   └── decodificadas/      ← WAV reconstruidos para medir
├── figuras/                ← espectrogramas diferenciales y curvas métrica vs. bitrate
├── resultados.csv
└── informe.pdf             ← reporte (también en .docx)
```

## Nota sobre métricas

`pip install visqol` no tiene rueda pre-compilada para nuestro entorno (Windows),
situación prevista en la consigna (§2.0 y §2.3). Se usan las métricas de respaldo:
**LSD** (todas las señales) y **STOI + PESQ** (voz). Está declarado en el informe.

## Licencias de las señales

- `music_tonal`: "Dance of the Sugar Plum Fairy" — Kevin MacLeod (CC-BY)
- `transitorios`: "Choice" — Admiral Bob (CC-BY)
- `voz`: narración LibriVox, "The Ashiel Mystery" (dominio público)
