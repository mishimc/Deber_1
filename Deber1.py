# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 19:25:52 2025

@author: PC
"""

#Librerías usadas
import requests_cache
import pandas as pd
import openmeteo_requests 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
from retry_requests import retry


#Obtención de la base de datos usando la API

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": -1.25,
	"longitude": -78.25,
	"hourly": ["soil_temperature_0cm", "soil_temperature_6cm", "soil_temperature_18cm", "soil_temperature_54cm", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "wind_speed_10m", "wind_speed_80m", "wind_speed_120m", "wind_speed_180m", "is_day"]
}
responses = openmeteo.weather_api(url, params=params)
# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_soil_temperature_0cm = hourly.Variables(0).ValuesAsNumpy()
hourly_soil_temperature_6cm = hourly.Variables(1).ValuesAsNumpy()
hourly_soil_temperature_18cm = hourly.Variables(2).ValuesAsNumpy()
hourly_soil_temperature_54cm = hourly.Variables(3).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(8).ValuesAsNumpy()
hourly_wind_speed_80m = hourly.Variables(9).ValuesAsNumpy()
hourly_wind_speed_120m = hourly.Variables(10).ValuesAsNumpy()
hourly_wind_speed_180m = hourly.Variables(11).ValuesAsNumpy()
hourly_is_day = hourly.Variables(12).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["soil_temperature_0cm"] = hourly_soil_temperature_0cm
hourly_data["soil_temperature_6cm"] = hourly_soil_temperature_6cm
hourly_data["soil_temperature_18cm"] = hourly_soil_temperature_18cm
hourly_data["soil_temperature_54cm"] = hourly_soil_temperature_54cm
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["wind_speed_80m"] = hourly_wind_speed_80m
hourly_data["wind_speed_120m"] = hourly_wind_speed_120m
hourly_data["wind_speed_180m"] = hourly_wind_speed_180m
hourly_data["is_day"] = hourly_is_day

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)#Base de datos 

#Analisis
print(hourly_dataframe.info())

# Convertir la columna de fecha a datetime
hourly_dataframe['date'] = pd.to_datetime(hourly_dataframe['date'])
# Columna solo con la fecha (sin la hora)
hourly_dataframe['fecha'] = hourly_dataframe['date'].dt.date 

#-------------------------------------------------------------------------------------
'''
Grafica para tiempos de temperatura promedio del suelo a 0cm por Dia
'''
# Agrupar por fecha y calcular el promedio diario
daily_temp = hourly_dataframe.groupby('fecha')['soil_temperature_0cm'].mean().reset_index()
plt.figure(figsize=(12, 6))
plt.plot(daily_temp['fecha'], daily_temp['soil_temperature_0cm'],marker='o', linestyle='-', color='brown', linewidth=2)
plt.title('Temperatura Promedio del Suelo a 0cm por Día', fontsize=14, fontweight='bold')
plt.xlabel('Fecha', fontsize=12)
plt.ylabel('Temperatura (°C)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
plt.gcf().autofmt_xdate()  # Rotar fechas 
plt.tight_layout()
plt.show()
plt.savefig('temperatura_suelo_diaria.png', dpi=300)


#---------------------------------------------------------------------------------------
'''
Promedios temperatura de suelo
'''

# Calcular promedios diarios para cada profundidad
daily_temp_0cm = hourly_dataframe.groupby('fecha')['soil_temperature_0cm'].mean().reset_index()
daily_temp_6cm = hourly_dataframe.groupby('fecha')['soil_temperature_6cm'].mean().reset_index()
daily_temp_18cm = hourly_dataframe.groupby('fecha')['soil_temperature_18cm'].mean().reset_index()
daily_temp_54cm = hourly_dataframe.groupby('fecha')['soil_temperature_54cm'].mean().reset_index()

# Crear el gráfico
plt.figure(figsize=(14, 7))

# Graficar las 4 series
plt.plot(daily_temp_0cm['fecha'], daily_temp_0cm['soil_temperature_0cm'], 
         marker='o', linestyle='-', color='brown', linewidth=2, label='0 cm')
plt.plot(daily_temp_6cm['fecha'], daily_temp_6cm['soil_temperature_6cm'], 
         marker='s', linestyle='-', color='green', linewidth=2, label='6 cm')
plt.plot(daily_temp_18cm['fecha'], daily_temp_18cm['soil_temperature_18cm'], 
         marker='^', linestyle='-', color='blue', linewidth=2, label='18 cm')
plt.plot(daily_temp_54cm['fecha'], daily_temp_54cm['soil_temperature_54cm'], 
         marker='D', linestyle='-', color='black', linewidth=2, label='54 cm')

# Configuración del gráfico (manteniendo tu estilo)
plt.title('Temperatura Promedio del Suelo a Diferentes Profundidades', fontsize=16, fontweight='bold')
plt.xlabel('Fecha', fontsize=12)
plt.ylabel('Temperatura (°C)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)

# Configurar el eje x como en tu código original
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
plt.gcf().autofmt_xdate()  # Rotar fechas

# Añadir leyenda
plt.legend(title='Profundidad:', fontsize=10, framealpha=1)

# Ajustar layout
plt.tight_layout()

# Mostrar y guardar el gráfico
plt.savefig('temperatura_suelo_multiprofundidad.png', dpi=300)
plt.show()

#-------------------------------------------------------------------------------
'''
Promedios velocidades de viento
'''
# Calcular promedios diarios para cada altura de viento
daily_wind_10m = hourly_dataframe.groupby('fecha')['wind_speed_10m'].mean().reset_index()
daily_wind_80m = hourly_dataframe.groupby('fecha')['wind_speed_80m'].mean().reset_index()
daily_wind_120m = hourly_dataframe.groupby('fecha')['wind_speed_120m'].mean().reset_index()
daily_wind_180m = hourly_dataframe.groupby('fecha')['wind_speed_180m'].mean().reset_index()

# Crear el gráfico
plt.figure(figsize=(14, 7))

# Graficar las 4 series de velocidad del viento
plt.plot(daily_wind_10m['fecha'], daily_wind_10m['wind_speed_10m'], 
         marker='o', linestyle='-', color='blue', linewidth=2, label='10 m')
plt.plot(daily_wind_80m['fecha'], daily_wind_80m['wind_speed_80m'], 
         marker='s', linestyle='-', color='green', linewidth=2, label='80 m')
plt.plot(daily_wind_120m['fecha'], daily_wind_120m['wind_speed_120m'], 
         marker='^', linestyle='-', color='red', linewidth=2, label='120 m')
plt.plot(daily_wind_180m['fecha'], daily_wind_180m['wind_speed_180m'], 
         marker='D', linestyle='-', color='purple', linewidth=2, label='180 m')

# Configuración del gráfico
plt.title('Velocidad Promedio del Viento a Diferentes Alturas', fontsize=16, fontweight='bold')
plt.xlabel('Fecha', fontsize=12)
plt.ylabel('Velocidad del Viento (m/s)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
plt.gcf().autofmt_xdate()  # Rotar fechas
plt.legend(title='Altura:', fontsize=10, framealpha=1)
plt.tight_layout()
plt.savefig('velocidad_viento_multialtura.png', dpi=300)
plt.show()


#--------------------------------------------------------------------------------------------
# Preparar datos para el heatmap para: Temperatura del Suelo por Profundidad y Hora del Día
hourly_dataframe['hora'] = hourly_dataframe['date'].dt.hour
temp_columns = ['soil_temperature_0cm', 'soil_temperature_6cm', 
               'soil_temperature_18cm', 'soil_temperature_54cm']

# Crear una tabla pivote para el heatmap
heatmap_data = hourly_dataframe.groupby('hora')[temp_columns].mean()

plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data.T, 
            cmap='coolwarm',
            annot=True, 
            fmt=".1f",
            linewidths=.5,
            cbar_kws={'label': 'Temperatura (°C)'})
plt.title('Temperatura del Suelo por Profundidad y Hora del Día', pad=20, fontsize=14)
plt.xlabel('Hora del Día')
plt.ylabel('Profundidad (cm)')
plt.yticks(ticks=[0.5, 1.5, 2.5, 3.5], labels=['0', '6', '18', '54'], rotation=0)
plt.tight_layout()
plt.savefig('heatmap_temperatura_suelo.png', dpi=300)
plt.show()

#---------------------------------------------------------------------------------------------------------
dates = hourly_data['date']
# Preparar datos para el heatmap de velocidad del viento
wind_columns = ['wind_speed_10m', 'wind_speed_80m', 
               'wind_speed_120m', 'wind_speed_180m']

heatmap_wind = hourly_dataframe.groupby('hora')[wind_columns].mean()

plt.figure(figsize=(12, 6))
sns.heatmap(heatmap_wind.T,
            cmap='YlOrBr',
            annot=True,
            fmt=".1f",
            linewidths=.5,
            cbar_kws={'label': 'Velocidad (m/s)'})
plt.title('Velocidad del Viento por Altura y Hora del Día', pad=20, fontsize=14)
plt.xlabel('Hora del Día')
plt.ylabel('Altura (m)')
plt.yticks(ticks=[0.5, 1.5, 2.5, 3.5], labels=['10', '80', '120', '180'], rotation=0)
plt.tight_layout()
plt.savefig('heatmap_velocidad_viento.png', dpi=300)
plt.show()
plt.figure(figsize=(12, 6))
#-------------------------------------------------------------------------------------------



# Crear subplots para cada profundidad
profundidades = {
    'soil_temperature_0cm': {'color': 'brown', 'label': '0 cm'},
    'soil_temperature_6cm': {'color': 'green', 'label': '6 cm'},
    'soil_temperature_18cm': {'color': 'blue', 'label': '18 cm'},
    'soil_temperature_54cm': {'color': 'black', 'label': '54 cm'}
}

for col, props in profundidades.items():
    plt.scatter(
        hourly_dataframe['date'].dt.hour,  # Hora del día
        hourly_dataframe[col],             # Temperatura
        color=props['color'],
        label=props['label'],
        alpha=0.5,
        s=20  # Tamaño de los puntos
    )

#-------------------------------------------------------------------------
# Gráfico de perfiles individuales para temperatura del suelo
plt.figure(figsize=(14, 7))
colors = ['#FF0000', '#00AAFF', '#FFA500', '#800080']  # Rojo, Azul, Naranja, Púrpura

# Dibujar cada profundidad como línea independiente
for (col, color) in zip(['soil_temperature_0cm', 'soil_temperature_6cm', 
                        'soil_temperature_18cm', 'soil_temperature_54cm'], colors):
    plt.plot(
        hourly_dataframe['date'], 
        hourly_dataframe[col], 
        label=col.replace('soil_temperature_', '').replace('cm', ' cm'), 
        color=color, 
        alpha=0.8,
        linewidth=2
    )

plt.title('Temperatura del Suelo por Profundidad (Perfiles Individuales)', fontsize=16)
plt.xlabel('Fecha y Hora', fontsize=12)
plt.ylabel('Temperatura (°C)', fontsize=12)
plt.legend(loc='upper left', title='Profundidad')
plt.grid(True, linestyle='--', alpha=0.5)
plt.gcf().autofmt_xdate(rotation=45)

plt.tight_layout()
plt.savefig('lineplot_temperaturas_profundidad.png', dpi=300)
plt.show()

#------------------------------------------------------------------------
# Gráfico de perfiles individuales para velocidad del viento
plt.figure(figsize=(14, 7))
colors = ['#FF0000', '#00AAFF', '#FFA500', '#800080']  # Rojo, Azul, Naranja, Púrpura

# Dibujar cada altura como línea independiente
for (col, color) in zip(['wind_speed_10m', 'wind_speed_80m', 
                        'wind_speed_120m', 'wind_speed_180m'], colors):
    plt.plot(
        hourly_dataframe['date'], 
        hourly_dataframe[col], 
        label=col.replace('wind_speed_', ''), 
        color=color, 
        alpha=0.8,
        linewidth=2
    )

plt.title('Velocidad del Viento por Altura (Perfiles Individuales)', fontsize=16)
plt.xlabel('Fecha y Hora', fontsize=12)
plt.ylabel('Velocidad (m/s)', fontsize=12)
plt.legend(loc='upper left', title='Altura:')
plt.grid(True, linestyle='--', alpha=0.5)
plt.gcf().autofmt_xdate(rotation=45)

plt.tight_layout()
plt.savefig('lineplot_velocidad_viento_altura.png', dpi=300)
plt.show()

#New