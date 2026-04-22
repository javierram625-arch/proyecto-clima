import pandas as pd

# Cargamos el archivo pesado
print("Leyendo archivo pesado... esto tardará un poco.")
df = pd.read_csv('GlobalLandTemperaturesByCity.csv')

# Filtramos solo lo que necesitamos para tu proyecto
paises_necesarios = ['Mexico', 'Argentina']
df_recortado = df[df['Country'].isin(paises_necesarios)]

# Guardamos la versión ligera (pesará unos 10-15 MB en lugar de 500)
df_recortado.to_csv('GlobalLandTemperaturesByCity.csv', index=False)
print("¡Listo! Archivo recortado con éxito.")