import pandas as pd

print("Cargando y filtrando datos para producción...")

# 1. GlobalTemperatures (Solo necesitamos años recientes para que cargue rápido)
df_global = pd.read_csv('GlobalTemperatures.csv')
df_global['dt'] = pd.to_datetime(df_global['dt'])
# Nos quedamos solo de 1850 en adelante (antes de eso hay muchos nulos)
df_global_recortado = df_global[df_global['dt'].dt.year >= 1850]
df_global_recortado.to_csv('GlobalTemperatures.csv', index=False)
print("✔ Datos Globales recortados.")

# 2. GlobalLandTemperaturesByCountry (Solo necesitamos México)
df_countries = pd.read_csv('GlobalLandTemperaturesByCountry.csv')
df_countries_mexico = df_countries[df_countries['Country'] == 'Mexico']
df_countries_mexico.to_csv('GlobalLandTemperaturesByCountry.csv', index=False)
print("✔ Datos por País recortados (Solo México).")

# 3. GlobalLandTemperaturesByCity (Confirmamos que solo sea México)
df_cities = pd.read_csv('GlobalLandTemperaturesByCity.csv')
df_cities_mexico = df_cities[df_cities['Country'] == 'Mexico']
df_cities_mexico.to_csv('GlobalLandTemperaturesByCity.csv', index=False)
print("✔ Datos por Ciudad recortados (Solo México).")

print("¡Listo! Ahora tus archivos pesan menos de 5MB en total. Render los va a amar.")