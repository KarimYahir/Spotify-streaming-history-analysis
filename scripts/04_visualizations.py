"""
Project:
    Spotify Streaming History Analysis

Script:
    04_visualizations.py

Description:
    Generates visualizations from the Spotify 2024 analysis, including
    top songs, monthly trends, monthly top-song cards, and a listening
    heatmap by weekday and hour.

Author:
    Karim Yahir Vallejo Flores
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mplcursors
from pathlib import Path

# Rutas del proyecto
data_path = Path("data/processed/spotify_2024.csv")
results_path = Path("results")
figures_path = Path("figures")
figures_path.mkdir(parents=True, exist_ok=True)

# Leer datos
datos_spotify = pd.read_csv(data_path)

# Preparar fechas y duración
datos_spotify["ts"] = pd.to_datetime(datos_spotify["ts"])
datos_spotify["fecha"] = datos_spotify["ts"].dt.date
datos_spotify["mes"] = datos_spotify["ts"].dt.to_period("M").astype(str)
datos_spotify["duration_min"] = datos_spotify["ms_played"] / 60000

# Top canciones
top_canciones = datos_spotify["master_metadata_track_name"].value_counts().head(20).reset_index()
top_canciones.columns = ["Canción", "Veces Escuchada"]

plt.figure(figsize=(6, 4))
ax = sns.barplot(
    x="Veces Escuchada",
    y="Canción",
    data=top_canciones,
    palette="Blues_r"
)

plt.xlabel("Número de Reproducciones")
plt.ylabel("Canción")
plt.title("Top 20 canciones más escuchadas en Spotify")
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.yticks(fontsize=5)

cursor = mplcursors.cursor(ax, hover=True)
cursor.connect("add", lambda sel: sel.annotation.set_text(f"{sel.target[0]:.0f} veces"))

plt.tight_layout()
plt.savefig(figures_path / "top_20_canciones.png", dpi=300)
plt.show()

# Canción más escuchada por mes
cancion_mes = datos_spotify.groupby(
    ["mes", "master_metadata_track_name", "master_metadata_album_artist_name"]
)["duration_min"].sum().reset_index()

cancion_mes = cancion_mes.sort_values(
    ["mes", "duration_min"],
    ascending=[True, False]
).drop_duplicates("mes")

for i, row in cancion_mes.iterrows():
    plt.figure(figsize=(6, 3))
    plt.axis("off")
    plt.title(f"{row['mes']} Wrapped", fontsize=14, weight="bold")
    plt.text(0.05, 0.7, f"Canción: {row['master_metadata_track_name']}", fontsize=12)
    plt.text(0.05, 0.5, f"Artista: {row['master_metadata_album_artist_name']}", fontsize=11)
    plt.text(0.05, 0.2, f"Minutos escuchados: {round(row['duration_min'], 1)}", fontsize=11)
    plt.tight_layout()
    plt.savefig(figures_path / f"wrapped_{row['mes']}.png", dpi=300)
    plt.close()

# Tendencia mensual
minutos_por_mes = datos_spotify.groupby("mes")["duration_min"].sum().reset_index()
minutos_por_mes.rename(columns={"duration_min": "Total_Minutos"}, inplace=True)

canciones_por_mes = datos_spotify.groupby("mes")["master_metadata_track_name"].count().reset_index()
canciones_por_mes.rename(columns={"master_metadata_track_name": "Total_Canciones"}, inplace=True)

tendencia_mensual = pd.merge(minutos_por_mes, canciones_por_mes, on="mes")

plt.figure(figsize=(8, 4))
plt.plot(tendencia_mensual["mes"], tendencia_mensual["Total_Minutos"], marker="o")
plt.title("Minutos escuchados por mes")
plt.xlabel("Mes")
plt.ylabel("Total de minutos")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(figures_path / "tendencia_minutos_por_mes.png", dpi=300)
plt.show()

# Mapa de calor
datos_spotify["hora"] = datos_spotify["ts"].dt.hour
datos_spotify["dia_semana"] = datos_spotify["ts"].dt.day_name()

orden_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
datos_spotify["dia_semana"] = pd.Categorical(
    datos_spotify["dia_semana"],
    categories=orden_dias,
    ordered=True
)

pivot_table = datos_spotify.pivot_table(
    index="dia_semana",
    columns="hora",
    values="duration_min",
    aggfunc="sum",
    fill_value=0
)

pivot_table.to_excel(results_path / "mapa_calor.xlsx", sheet_name="Mapa calor")

plt.figure(figsize=(14, 6))
sns.heatmap(
    pivot_table,
    cmap="YlGnBu",
    linewidths=0.5,
    annot=False
)

plt.title("Mapa de Calor: Minutos escuchados por día de la semana y hora")
plt.xlabel("Hora del día")
plt.ylabel("Día de la semana")
plt.tight_layout()
plt.savefig(figures_path / "mapa_calor_spotify.png", dpi=300)
plt.show()