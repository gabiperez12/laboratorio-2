# graficar.py
import os
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Lee resultados.csv y genera las figuras del informe:
#  - LSD vs bitrate (una figura por senal, curva AAC vs Opus)
#  - STOI vs bitrate (solo voz)
#  - PESQ vs bitrate (solo voz)
#  - bitrate real vs bitrate objetivo (todas las senales)

CSV = "resultados.csv"
FIG_DIR = "figuras"
os.makedirs(FIG_DIR, exist_ok=True)

# cargar la tabla en una lista de diccionarios
filas = []
with open(CSV, newline="") as f:
    for fila in csv.DictReader(f):
        filas.append(fila)

senales = sorted(set(f["senal"] for f in filas))
codecs = ["AAC", "Opus"]
colores = {"AAC": "tab:blue", "Opus": "tab:orange"}

def curva(senal, codec, columna):
    # devuelve (bitrates, valores) ordenados por bitrate para una senal y codec
    pares = [(int(f["bitrate"]), float(f[columna]))
             for f in filas
             if f["senal"] == senal and f["codec"] == codec and f[columna] != ""]
    pares.sort()
    return [p[0] for p in pares], [p[1] for p in pares]

# 1) LSD vs bitrate, una figura por senal
for senal in senales:
    plt.figure(figsize=(6,4))
    for codec in codecs:
        x, y = curva(senal, codec, "LSD")
        plt.plot(x, y, "o-", color=colores[codec], label=codec)
    plt.xlabel("Bitrate objetivo (kbps)")
    plt.ylabel("LSD (dB)")
    plt.title(f"LSD vs bitrate — {senal}")
    plt.xticks([24, 64, 128])
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, f"lsd_vs_bitrate_{senal}.png"), dpi=120)
    plt.close()

# 2) STOI vs bitrate (solo voz)
plt.figure(figsize=(6,4))
for codec in codecs:
    x, y = curva("voz", codec, "STOI")
    plt.plot(x, y, "o-", color=colores[codec], label=codec)
plt.xlabel("Bitrate objetivo (kbps)")
plt.ylabel("STOI")
plt.title("STOI vs bitrate — voz")
plt.xticks([24, 64, 128])
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "stoi_vs_bitrate_voz.png"), dpi=120)
plt.close()

# 3) PESQ vs bitrate (solo voz)
plt.figure(figsize=(6,4))
for codec in codecs:
    x, y = curva("voz", codec, "PESQ")
    plt.plot(x, y, "o-", color=colores[codec], label=codec)
plt.xlabel("Bitrate objetivo (kbps)")
plt.ylabel("PESQ (MOS-LQO)")
plt.title("PESQ vs bitrate — voz")
plt.xticks([24, 64, 128])
plt.ylim(1, 5)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "pesq_vs_bitrate_voz.png"), dpi=120)
plt.close()

# 4) Bitrate real vs objetivo (todas las senales, un marcador por punto)
plt.figure(figsize=(6,4))
marcadores = {"music_tonal": "o", "voz": "s", "transitorios": "^"}
for senal in senales:
    for codec in codecs:
        x, y = curva(senal, codec, "br_real")
        plt.plot(x, y, marcadores[senal], color=colores[codec],
                 label=f"{codec} — {senal}")
plt.plot([0, 140], [0, 140], "k--", alpha=0.5, label="ideal (real = objetivo)")
plt.xlabel("Bitrate objetivo (kbps)")
plt.ylabel("Bitrate real (kbps)")
plt.title("Bitrate real vs objetivo")
plt.grid(True, alpha=0.3)
plt.legend(fontsize=7)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "bitrate_real_vs_objetivo.png"), dpi=120)
plt.close()

print(f"Figuras guardadas en '{FIG_DIR}/'")
