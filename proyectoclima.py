import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

def limpiar_coordenadas(coord):
    if isinstance(coord, str):
        valor = float(coord[:-1])
        if coord[-1] in ['S', 'W']:
            valor = -valor
        return valor
    return coord

app = dash.Dash(__name__)
app.title = "Análisis Climático - Javier Ramírez"
server = app.server 

df_global = pd.read_csv('GlobalTemperatures.csv')
df_countries = pd.read_csv('GlobalLandTemperaturesByCountry.csv')
df_ciudades = pd.read_csv('GlobalLandTemperaturesByCity.csv')

df_global['dt'] = pd.to_datetime(df_global['dt'])
df_global = df_global.dropna(subset=['LandAverageTemperature'])
df_global['Year'] = df_global['dt'].dt.year
global_yearly = df_global.groupby('Year')['LandAverageTemperature'].mean().reset_index()

df_mexico = df_countries[df_countries['Country'] == 'Mexico'].copy()
df_mexico['dt'] = pd.to_datetime(df_mexico['dt'])
df_mexico = df_mexico.dropna(subset=['AverageTemperature'])
df_mexico['Year'] = df_mexico['dt'].dt.year
mexico_yearly = df_mexico.groupby('Year')['AverageTemperature'].mean().reset_index()

baseline = mexico_yearly[(mexico_yearly['Year'] >= 1850) & (mexico_yearly['Year'] <= 1950)]['AverageTemperature'].mean()
mexico_yearly['Trend'] = mexico_yearly['AverageTemperature'].rolling(window=10).mean()

df_ciudades_mx = df_ciudades[df_ciudades['Country'] == 'Mexico'].copy()
df_ciudades_mx['dt'] = pd.to_datetime(df_ciudades_mx['dt'])
df_ciudades_mx = df_ciudades_mx.dropna(subset=['AverageTemperature'])
df_ciudades_mx['Year'] = df_ciudades_mx['dt'].dt.year
df_ciudades_mx['Lat'] = df_ciudades_mx['Latitude'].apply(limpiar_coordenadas)
df_ciudades_mx['Lon'] = df_ciudades_mx['Longitude'].apply(limpiar_coordenadas)

df_mapa = df_ciudades_mx[df_ciudades_mx['Year'] >= 1900].copy() 
df_anim = df_mapa.groupby(['Year', 'City', 'Lat', 'Lon'])['AverageTemperature'].mean().reset_index()
df_anim = df_anim.sort_values('Year')

ciudades_clave = ['Monterrey', 'León', 'Mexico',  "Mérida"] 
df_regiones_anim = df_anim[df_anim['City'].isin(ciudades_clave)].copy()
df_regiones_anim = df_regiones_anim.sort_values(['Year', 'City'])

# --- PROCESAMIENTO: MAPA MUNDIAL ---
df_paises = df_countries.copy()
df_paises['dt'] = pd.to_datetime(df_paises['dt'])
df_paises = df_paises.dropna(subset=['AverageTemperature'])
df_paises['Year'] = df_paises['dt'].dt.year
df_paises_anim = df_paises[df_paises['Year'] >= 1900].groupby(['Year', 'Country'])['AverageTemperature'].mean().reset_index()
df_paises_anim = df_paises_anim.sort_values(['Year', 'Country'])


# --- GRÁFICAS ---

# Gráfica 1: Contexto Mundial
fig_global = px.line(global_yearly, x='Year', y='LandAverageTemperature',
                     title='Tendencia Térmica Global (1750-2015)',
                     labels={'LandAverageTemperature': 'Temperatura (°C)', 'Year': 'Año'},
                     template="plotly_white")
fig_global.update_traces(line_color='#d32f2f', line_width=2)

# Gráfica 2: Registro Anual México (Datos Crudos)
fig_anual_mex = px.line(mexico_yearly, x='Year', y='AverageTemperature',
                        title='Registros de Temperatura Anual en México (Datos Crudos)',
                        labels={'AverageTemperature': 'Temperatura Anual (°C)', 'Year': 'Año'},
                        template="plotly_white")
fig_anual_mex.update_traces(line_color='#1976d2', line_width=1.5)

# Gráfica 3: El Punto de Inflexión Nacional (Tendencia)
fig_inflexion = px.line(mexico_yearly, x='Year', y='Trend',
                        title='Análisis del Punto de Inflexión Climático en México',
                        labels={'Trend': 'Temperatura Nacional (°C)', 'Year': 'Año'},
                        template="plotly_white")
fig_inflexion.update_traces(line_color='#f57c00', line_width=3)
fig_inflexion.add_hline(y=baseline, line_dash="dash", line_color="#388e3c", 
                        annotation_text=f"Promedio Histórico: {baseline:.2f}°C", 
                        annotation_position="bottom right")

# Gráfica 4: MAPA REGIONAL
fig_regiones = px.scatter_mapbox(
    df_regiones_anim, lat='Lat', lon='Lon', 
    color='AverageTemperature', size='AverageTemperature',
    text='City', 
    animation_frame='Year',
    animation_group='City',
    center=dict(lat=23.6345, lon=-102.5528), zoom=4,
    mapbox_style="carto-positron",
    title="Impacto Regional: Norte, Centro y Sur",
    labels={'AverageTemperature': 'Temp. (°C)', 'Year': 'Año', 'City': 'Ciudad'},
    color_continuous_scale="YlOrRd", range_color=[15, 28],
    size_max=35 
)
fig_regiones.update_traces(textposition='top right', textfont=dict(size=14, color='#2c3e50', family="Arial Black"))
fig_regiones.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

# Gráfica 5: Mapa de Densidad Nacional
fig_densidad = px.density_mapbox(
    df_anim, lat='Lat', lon='Lon', z='AverageTemperature', 
    radius=25, center=dict(lat=23.6345, lon=-102.5528), zoom=3.8,
    mapbox_style="carto-positron", animation_frame="Year",
    title="Ola de calor en México año tras año desde 1900 hasta el 2013",
    labels={'AverageTemperature': 'Temp. Promedio (°C)', 'Year': 'Año', 'City': 'Ciudad'},
    color_continuous_scale="YlOrRd", range_color=[15, 27]
)
fig_densidad.update_layout(margin={"r":0,"t":50,"l":0,"b":0})


geojson_url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"

fig_mundial = px.choropleth_mapbox(
    df_paises_anim,
    geojson=geojson_url,
    locations="Country",
    featureidkey="properties.name", 
    color="AverageTemperature",
    hover_name="Country",
    animation_frame="Year",
    color_continuous_scale="YlOrRd", 
    title="Evolución Térmica por País (1900-2013)",
    range_color=[0, 30],
    mapbox_style="carto-positron",  
    zoom=1.2,                       
    center={"lat": 20.0, "lon": 0.0}, 
    labels={'AverageTemperature': 'Temp. Promedio (°C)',
            'Year': 'Año',
            'Country': 'País'}
)
fig_mundial.update_layout(margin={"r":0,"t":50,"l":0,"b":0})


# --- LAYOUT ---
app.layout = html.Div(style={'backgroundColor': '#f4f7f6', 'padding': '40px 20px', 'fontFamily': 'Segoe UI, Roboto, Helvetica, Arial, sans-serif'}, children=[
    
    html.Div(style={'maxWidth': '950px', 'margin': 'auto', 'backgroundColor': 'white', 'padding': '40px', 'borderRadius': '12px', 'boxShadow': '0 4px 15px rgba(0,0,0,0.05)'}, children=[
        
        html.H1("¿Cuándo dejó de ser normal el calor en México?", style={'color': '#2c3e50', 'textAlign': 'center', 'fontWeight': '800'}),
        html.P("Temperatura histórica global y en México", style={'textAlign': 'center', 'fontSize': '1.2rem', 'color': '#7f8c8d', 'marginBottom': '30px'}),
        html.Hr(style={'borderColor': '#ecf0f1', 'marginBottom': '30px'}),
        
        html.H2("1. El Gran Cuadro: Un planeta que se calienta", style={'color': '#2c3e50'}),
        html.P("¿Desde cuándo se calentó el mundo? Antes de analizar a México, observa el planeta. Esta gráfica demuestra cómo la temperatura de la Tierra mantuvo cierta estabilidad histórica hasta cruzar un punto crítico.", style={'color': '#555', 'lineHeight': '1.6'}),
        dcc.Graph(figure=fig_global),

        html.H2("2. Registros Históricos: La Volatilidad de México", style={'marginTop': '50px', 'color': '#2c3e50'}),
        html.P("¿Por qué es tan difícil percibir el cambio climático a simple vista? Los registros anuales en México muestran una volatilidad extrema. Estos picos y valles representan variaciones climáticas naturales que actúan como 'ruido' estadístico, enmascarando la verdadera tendencia del calentamiento.", style={'color': '#555', 'lineHeight': '1.6'}),
        dcc.Graph(figure=fig_anual_mex),

        html.H2("3. El Hallazgo: Cruzando el punto de no retorno", style={'marginTop': '50px', 'color': '#2c3e50'}),
        html.P("¿En qué año México cruzó el punto de no retorno? Al aplicar un promedio de 10 años a los datos, el 'ruido' desaparece. Aquí es evidente cómo la temperatura nacional superó permanentemente su promedio histórico y no ha vuelto a bajar.", style={'color': '#555', 'lineHeight': '1.6'}),
        dcc.Graph(figure=fig_inflexion),
        
        html.H2("4. Contrastes Regionales: Evolución por Ciudad", style={'marginTop': '50px', 'color': '#2c3e50'}),
        html.P("¿Se calienta igual el norte, el centro y el sur de México? En esta visualizacion se toman ciudades claves, para poder respresentar como el cambio climatico afecta el pais en la zona norte, centro y sur al pasar los años.", style={'color': '#555', 'lineHeight': '1.6'}),
        dcc.Graph(figure=fig_regiones),

        html.Hr(style={'borderColor': '#ecf0f1', 'margin': '50px 0'}),
        html.H2("5. Visualización Geo-Temporal: La Ola de Calor al pasar de los años en el país", style={'color': '#2c3e50'}),
        html.P("¿Cómo se expande una crisis térmica por el México? Más allá de ciudades individuales, este mapa de densidad ilustra la consolidación de bloques de calor en varios puntos del país.", style={'lineHeight': '1.6', 'color': '#555'}),
        dcc.Graph(figure=fig_densidad),
        
        # --- NUEVA SECCIÓN GLOBAL ---
        html.Hr(style={'borderColor': '#ecf0f1', 'margin': '50px 0'}),
        html.H2("6. Perspectiva Global: El avance del calor por países", style={'color': '#2c3e50'}),
        html.P("¿Es esta emergencia climática exclusiva de México? Esta es una representacion a nivel global por paises, de como evoluciona el cambio climatico en forma de linea de tiempo desde 1900 hasta el 2013.", style={'lineHeight': '1.6', 'color': '#555'}),
        dcc.Graph(figure=fig_mundial),
        
        html.Div(style={
            'backgroundColor': '#e8f6f3', 'padding': '35px', 'borderRadius': '10px', 'marginTop': '60px', 
            'borderLeft': '6px solid #1abc9c', 'boxShadow': '0 4px 10px rgba(0,0,0,0.03)'
        }, children=[
            html.H3("Conclusión: El Nuevo Paradigma Climático", style={'margin': '0 0 15px 0', 'color': '#16a085', 'fontWeight': 'bold', 'fontSize': '1.5rem'}),
            html.P("A través de este recorrido visual, la respuesta a nuestra pregunta inicial es irrefutable: el calor en México dejó de ser 'normal' en el momento en que la tendencia matemática rompió permanentemente su promedio histórico (1850-1950). Las visualizaciones demuestran que ya no nos enfrentamos a años atípicamente calurosos provocados por la volatilidad natural, sino a un desplazamiento estructural de todo el sistema climático.", style={'color': '#2c3e50', 'lineHeight': '1.8', 'fontSize': '1.1rem'})
        ]),
    ]),
        
    html.Footer([
        html.Div([
            html.P(["Fuente de datos original: ", html.A("Berkeley Earth (Kaggle)", href="https://www.kaggle.com/datasets/berkeleyearth/climate-change-earth-surface-temperature-data", target="_blank", style={'color': '#2980b9', 'textDecoration': 'none', 'fontWeight': 'bold'})], style={'margin': '0'}),
            html.P("Fecha de extracción: 22 de abril de 2026", style={'margin': '5px 0 0 0'})
        ], style={'textAlign': 'center', 'marginTop': '60px', 'fontSize': '0.85rem', 'color': '#7f8c8d', 'borderTop': '1px solid #ecf0f1', 'paddingTop': '20px'}),
        html.P("Javier Alejandro Ramírez López | Ingeniería en Inteligencia Artificial", style={'textAlign': 'center', 'marginTop': '20px', 'fontWeight': 'bold', 'color': '#7f8c8d'}),
        html.P("Universidad Iberoamericana León", style={'textAlign': 'center', 'color': '#95a5a6'})
    ])
])

if __name__ == '__main__':
    app.run(debug=True)