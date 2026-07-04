"""
Project:
    Spotify Streaming History Analysis

Script:
    02_basic_statistics.py

Description:
    Loads the cleaned Spotify 2024 dataset and calculates basic
    descriptive statistics: top songs, top albums, top artists,
    total listening time, monthly activity, and daily listening summary.

Author:
    Karim Yahir Vallejo Flores
"""

import pandas as pd
from pathlib import Path

# Rutas del proyecto
input_path = Path("data/processed/spotify_2024.csv")
results_path = Path("results")
results_path.mkdir(parents=True, exist_ok=True)

# Cargar datos
datos_spotify = pd.read_csv(input_path)

# Convertir timestamps a fecha
datos_spotify["ts"] = pd.to_datetime(datos_spotify["ts"])
datos_spotify["fecha"] = datos_spotify["ts"].dt.date
datos_spotify["mes"] = datos_spotify["ts"].dt.to_period("M").astype(str)

# Calcular duración en minutos
datos_spotify["duration_min"] = datos_spotify["ms_played"] / 60000

# Top canciones
top_canciones = datos_spotify["master_metadata_track_name"].value_counts().head(20).reset_index()
top_canciones.columns = ["Canción", "Veces Escuchada"]
print("\nTop canciones:")
print(top_canciones)
top_canciones.to_excel(results_path / "top_canciones.xlsx", sheet_name="Top Canciones", index=False)

# Top álbumes
top_albumes = datos_spotify["master_metadata_album_album_name"].value_counts().head(10).reset_index()
top_albumes.columns = ["Album", "Veces escuchadas_album"]
print("\nTop álbumes:")
print(top_albumes)
top_albumes.to_excel(results_path / "top_albumes.xlsx", sheet_name="Top Albumes", index=False)

# Tiempo total escuchado
total_ms = datos_spotify["ms_played"].sum()
total_minutos = total_ms / 60000
total_horas = total_ms / (1000 * 60 * 60)

print(f"\nTotal de horas de música: {total_horas:.2f} h")
print(f"Total de minutos escuchados: {total_minutos:.2f}")

resumen = pd.DataFrame({
    "Métrica": ["Total de minutos escuchados", "Total de horas de música"],
    "Valor": [round(total_minutos, 2), round(total_horas, 2)]
})

resumen.to_excel(results_path / "resumen_tiempo_escuchado.xlsx", sheet_name="Resumen", index=False)

# Top artistas
top_artistas = datos_spotify["master_metadata_album_artist_name"].value_counts().head(20).reset_index()
top_artistas.columns = ["Artista", "Veces Escuchada del artista durante el año"]
print("\nTop artistas:")
print(top_artistas)
top_artistas.to_excel(results_path / "top_artistas.xlsx", sheet_name="Top Artistas", index=False)

# Canciones escuchadas por mes
canciones_mes = datos_spotify["mes"].value_counts().sort_index().reset_index()
canciones_mes.columns = ["mes", "Número de canciones escuchadas"]
print("\nCanciones escuchadas por mes:")
print(canciones_mes)
canciones_mes.to_excel(results_path / "canciones_mes.xlsx", sheet_name="Canciones por mes", index=False)

# Tendencia mensual
minutos_por_mes = datos_spotify.groupby("mes")["duration_min"].sum().reset_index()
minutos_por_mes.rename(columns={"duration_min": "Total_Minutos"}, inplace=True)

canciones_por_mes = datos_spotify.groupby("mes")["master_metadata_track_name"].count().reset_index()
canciones_por_mes.rename(columns={"master_metadata_track_name": "Total_Canciones"}, inplace=True)

tendencia_mensual = pd.merge(minutos_por_mes, canciones_por_mes, on="mes")

tendencia_mensual["Crec_Minutos_%"] = tendencia_mensual["Total_Minutos"].pct_change() * 100
tendencia_mensual["Crec_Canciones_%"] = tendencia_mensual["Total_Canciones"].pct_change() * 100

print("\nTendencia mensual:")
print(tendencia_mensual)
tendencia_mensual.to_excel(results_path / "tendencia_mensual.xlsx", sheet_name="Tendencia mensual", index=False)

# Canción más escuchada de cada mes
cancion_mes = datos_spotify.groupby(
    ["mes", "master_metadata_track_name", "master_metadata_album_artist_name"]
)["duration_min"].sum().reset_index()

cancion_mes = cancion_mes.sort_values(
    ["mes", "duration_min"],
    ascending=[True, False]
).drop_duplicates("mes")

print("\nCanción más escuchada de cada mes:")
print(cancion_mes[["mes", "master_metadata_track_name", "master_metadata_album_artist_name", "duration_min"]])

cancion_mes.to_excel(results_path / "cancion_top_por_mes.xlsx", sheet_name="Canción por mes", index=False)

# Resumen de días escuchados
escucha_por_dia = datos_spotify.groupby("fecha")["ms_played"].sum() / 60000

dia_top = escucha_por_dia.idxmax()
dia_top_min = escucha_por_dia.idxmin()
minutos_top = escucha_por_dia.max()
minutos_top_min = escucha_por_dia.min()

resumen_dias_escuchados = pd.DataFrame({
    "Día mas escuchado": [dia_top],
    "Minutos del día mas escuchado": [round(minutos_top, 2)],
    "Día menos escuchado": [dia_top_min],
    "Minutos del día menos escuchado": [round(minutos_top_min, 2)]
})

print("\nResumen de días escuchados:")
print(resumen_dias_escuchados)

resumen_dias_escuchados.to_excel(
    results_path / "resumen_dias_escuchados.xlsx",
    sheet_name="Resumen días",
    index=False
)

print(f"\nEl día que más escuchaste música fue {dia_top} con {minutos_top:.2f} minutos.")
print(f"El día que menos escuchaste música fue {dia_top_min} con {minutos_top_min:.2f} minutos.")