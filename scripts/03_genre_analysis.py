"""
Project:
    Spotify Streaming History Analysis

Script:
    03_genre_analysis.py

Description:
    Uses the Spotify API to obtain artist genres, adds genre information
    to the 2024 Spotify dataset, and calculates the most listened genre
    by month.

Author:
    Karim Yahir Vallejo Flores
"""

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
from pathlib import Path

# Rutas del proyecto
input_path = Path("data/processed/spotify_2024.csv")
results_path = Path("results")
figures_path = Path("figures")

results_path.mkdir(parents=True, exist_ok=True)
figures_path.mkdir(parents=True, exist_ok=True)

# Leer datos
datos_spotify = pd.read_csv(input_path)

# Autenticación a la API de Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id='TU CLIENT_ID',
    client_secret='TU CLIENT_SECRET'
))

# Preparar datos
datos_spotify["ts"] = pd.to_datetime(datos_spotify["ts"])
datos_spotify["mes"] = datos_spotify["ts"].dt.to_period("M")

genres_cache = {}

# Función para obtener géneros de un artista
def get_genre(master_metadata_album_artist_name):
    global genres_cache

    if pd.isna(master_metadata_album_artist_name):
        return []

    if master_metadata_album_artist_name in genres_cache:
        return genres_cache[master_metadata_album_artist_name]

    print(f"Buscando géneros de: {master_metadata_album_artist_name}")

    try:
        result = sp.search(q="artist:" + master_metadata_album_artist_name, type="artist")

        if result["artists"]["items"]:
            genres = result["artists"]["items"][0]["genres"]
        else:
            genres = []

    except Exception as e:
        print(f"Error al buscar géneros para {master_metadata_album_artist_name}: {e}")
        time.sleep(1)
        genres = []

    genres_cache[master_metadata_album_artist_name] = genres
    return genres

# Añadir géneros al DataFrame
datos_spotify["genres"] = datos_spotify["master_metadata_album_artist_name"].apply(get_genre)

# Expandir los géneros
datos_spotify_genres = datos_spotify.explode("genres")

# Filtrar filas sin género
datos_spotify_genres = datos_spotify_genres[
    datos_spotify_genres["genres"].notna() &
    (datos_spotify_genres["genres"] != "")
]

# Calcular duración en minutos
datos_spotify_genres["duration_min"] = datos_spotify_genres["ms_played"] / 60000

# Agrupar por mes y género
genero_mes = datos_spotify_genres.groupby(
    ["mes", "genres"],
    as_index=False
)["duration_min"].sum()

# Encontrar el género más escuchado por mes
genero_top = genero_mes.loc[
    genero_mes.groupby("mes")["duration_min"].idxmax()
]

genero_top = genero_top.sort_values("mes")

# Mostrar resultado
print("Género más escuchado por mes:")
print(genero_top[["mes", "genres", "duration_min"]])

# Guardar resultados
genero_top.to_excel(
    results_path / "genero_top.xlsx",
    sheet_name="Genero musical",
    index=False
)