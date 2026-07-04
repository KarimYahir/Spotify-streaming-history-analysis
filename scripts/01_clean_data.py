"""
Project:
    Spotify Streaming History Analysis

Script:
    01_clean_data.py

Description:
    Loads Spotify JSON files, merges them into a single DataFrame,
    filters the records corresponding to 2024,
    cleans missing values,
    and exports the processed dataset as a CSV file.

Author:
    Karim Yahir Vallejo Flores
"""

import pandas as pd
import json
import os
from pathlib import Path

#Nota principal. Leer todos los archivos JSON exportados por Spotify

# Rutas del proyecto
raw_data_path = Path("data/raw")
processed_data_path = Path("data/processed")
output_path = processed_data_path / "spotify_2024.csv"

# Cargar todos los archivos JSON de la carpeta data/raw
dataframes = []

#Si quieres ver los archivos que se van a procesar, puedes descomentar la siguiente línea:
""""
for file_path in raw_data_path.glob("*"):
    print(file_path)
"""

for file_path in raw_data_path.glob("*"):
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    df_temp = pd.json_normalize(data)
    dataframes.append(df_temp)

# Concatenar los DataFrames
df = pd.concat(dataframes, ignore_index=True) 

# Filtrar solo los datos de 2024
df["ts"] = pd.to_datetime(df["ts"])
df_2024 = df[df["ts"].dt.year == 2024].copy()

# Eliminar registros sin nombre de canción
df_2024.dropna(subset=["master_metadata_track_name"], inplace=True)

# Rellenar valores faltantes
# En columnas de texto usamos "Unknown" para no mezclar texto con números.
text_columns = df_2024.select_dtypes(include="object").columns
df_2024[text_columns] = df_2024[text_columns].fillna("Unknown")

# En columnas numéricas usamos 0.
numeric_columns = df_2024.select_dtypes(include="number").columns
df_2024[numeric_columns] = df_2024[numeric_columns].fillna(0)

# Guardar CSV
processed_data_path.mkdir(parents=True, exist_ok=True)
df_2024.to_csv(output_path, index=False)

# Verificar si el archivo fue guardado correctamente
if os.path.exists(output_path):
    print(f"El archivo fue guardado correctamente en: {output_path}")
else:
    print("Hubo un problema al guardar el archivo.")

