#1.LIBRERIAS
import numpy as np
import pandas as pd
import pickle
import math
import streamlit as st

from sklearn.preprocessing import OneHotEncoder

from sklearn.linear_model import Ridge

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline

#2.CARGA DATOS

# -------------------- DATOS METEOROLÓGICOS ------------------------------

# Cargar un archivo con los datos meteorológicos a analizar
archivo = st.file_uploader('Selecciona un archivo csv')

if archivo is not None:
    df = pd.read_csv(archivo)
else:
    st.stop()

variable_num = st.selectbox('Selecciona una variable numerica:',df.columns.to_list())

fig, ax = plt.subplots()

ax = sns.histplot(data = df, x = variable_num)

st.pyplot(fig)


# -------------------- CRITERIOS TRABAJO VEHÍCULOS ------------------------------
# Quitamos este código porque estos datos los introduciremos a mano en la pantalla de la app
# base_path = path + '/01_Documentos/Criterios_trabajo_transportes.csv'
# df_transport_data = pd.read_csv(base_path, sep=';')


# -------------------- DATOS PARQUES EÓLICOS ------------------------------
# Quitamos este código porque estos datos los introduciremos a mano en la pantalla de la app
# base_path = path + '/01_Documentos/Criterios_parques_eolicos.csv'
# df_osw_data = pd.read_csv(base_path, sep=';')


#3.VARIABLES Y REGISTROS FINALES
df['date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])


#4.FUNCIONES DE SOPORTE

# ----------------------- DATOS METEOROLÓGICOS -------------------------------------------------

# Lista de variables binarias
binarias = ['Ice_coverage', 'Lightning', 'Heli_blade_icing', 'VFR_cloud', 'Categorical_snow']

# Seleccionar solo las columnas de tipo 'object' (que podrían tener decimales como texto)
object_columns = df.select_dtypes(include=['object']).columns

# Aplicar la transformación solo a las columnas numéricas que estén en formato de texto
for col in object_columns:
    try:
        # Reemplazar comas por puntos y convertir a float
        df[col] = df[col].str.replace(',', '.').astype(float)
        
    except ValueError:
        # Si hay un error de conversión, dejamos la columna como está
        print(f"No se pudo convertir la columna {col} a float.")

# Convertir la variable 'Date' a formato datetime
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Convertir las variables binarias a int
for col in binarias:
    if col in df.columns:
        df[col] = df[col].astype(int)
    else:
        print(f"La columna {col} no existe en el DataFrame")
        
        
# ----------------------- DATOS VEHÍCULOS -------------------------------------------------
# Lista de columnas a transformar
columns_to_transform = ['Visibility (km)', 'Wave limit (Hs) (m)']

# Iterar sobre cada columna y aplicar la transformación
for column in columns_to_transform:
    df_transport_data[column] = df_transport_data[column].str.replace(',', '.').astype(float)
    
    
# ----------------------- DATOS PARQUES EÓLICOS -------------------------------------------------
# Lista de columnas a transformar
columns_to_transform = ['Load Factor','Energy price (€/KWhr)','Productivity target',
                        'Failure rate','Cost tech/day']

# Iterar sobre cada columna y aplicar la transformación
for column in columns_to_transform:
    df_osw_data[column] = df_osw_data[column].str.replace(',', '.').astype(float)
    

# Lista de columnas con las localizaciones
location_columns = ['Location_OSW', 'Location sea_port', 'Location heli_port']
# Lista de nombres de nuevas columnas para latitud y longitud
lat_lon_columns = [('lat_OSW', 'lon_OSW'), ('lat_sea_port', 'lon_sea_port'), ('lat_heli_port', 'lon_heli_port')]

# Iterar sobre las columnas de ubicación y las nuevas columnas de latitud y longitud
for loc_col, (lat_col, lon_col) in zip(location_columns, lat_lon_columns):
    # Separar latitud y longitud
    df_osw_data[[lat_col, lon_col]] = df_osw_data[loc_col].str.split(',', expand=True)
    
    # Convertir a tipo float
    df_osw_data[lat_col] = df_osw_data[lat_col].astype(float)
    df_osw_data[lon_col] = df_osw_data[lon_col].astype(float)
    

# Diccionario de localizaciones
locations = {
    'golfo_vizcaya': 'Viz_23',
    'mar_norte': 'Nor_22',
    'mar_baltico': 'Bal_24'}

# Asignar los valores a cada DataFrame para cada localización
for location, name in locations.items():
    # Filtrar los datos de df_osw_data para la turbina correspondiente
    data = df_osw_data[df_osw_data['Name'] == name].iloc[0]

    # Asignar los valores al DataFrame correspondiente en la fila
    df.loc[df['location'] == location, 'wtg'] = data['Nº WTG']
    df.loc[df['location'] == location, 'power_wtg'] = data['Power/WTG (MW)']
    df.loc[df['location'] == location, 'load_factor'] = data['Load Factor']
    df.loc[df['location'] == location, 'energy_price'] = data['Energy price (€/KWhr)']
    df.loc[df['location'] == location, 'lost_energy_price'] = data['Lost energy price']
    df.loc[df['location'] == location, 'surplus_energy_price'] = data['Surplus energy price']
    df.loc[df['location'] == location, 'prod_target'] = data['Productivity target']
    df.loc[df['location'] == location, 'fr'] = data['Failure rate']
    df.loc[df['location'] == location, 'corrective'] = data['Corrective mean time (hours)']
    df.loc[df['location'] == location, 'go_window'] = data['Go Window']  # Corrige el nombre de la columna
    df.loc[df['location'] == location, 'preventive'] = data['Preventive WTG/year']
    df.loc[df['location'] == location, 'lat_OSW'] = data['lat_OSW']
    df.loc[df['location'] == location, 'lon_OSW'] = data['lon_OSW']
    df.loc[df['location'] == location, 'lat_sea_port'] = data['lat_sea_port']
    df.loc[df['location'] == location, 'lon_sea_port'] = data['lon_sea_port']
    df.loc[df['location'] == location, 'lat_heli_port'] = data['lat_heli_port']
    df.loc[df['location'] == location, 'lon_heli_port'] = data['lon_heli_port']

# Actualizar el DataFrame
df_updated = df

# Guardamos el dato de 'Cost €/day' para cada vehículo
ctv_cost = df_transport_data.loc[df_transport_data['Transport'] == 'CTV', 'Cost €/day'].values[0]
sov_cost = df_transport_data.loc[df_transport_data['Transport'] == 'SOV', 'Cost €/day'].values[0]
heli_cost = df_transport_data.loc[df_transport_data['Transport'] == 'Helicopter', 'Cost €/day'].values[0]

# Creamos la columna '*_day_cost' con los costes correspondientes de cada vehículo al día
df['ctv_day_cost'] = ctv_cost
df['sov_day_cost'] = sov_cost
df['heli_day_cost'] = heli_cost


# ------------------------------ CTV -------------------------------------------------

# Criterios trabajo transportes

ctv_visibility = df_transport_data.loc[df_transport_data['Transport'] == 'CTV', 'Visibility (km)'].values[0]
ctv_wind_speed_150m = df_transport_data.loc[df_transport_data['Transport'] == 'CTV', 'Wind Limit to Work (technicians) (m/s)'].values[0]
ctv_sign_wave_height = df_transport_data.loc[df_transport_data['Transport'] == 'CTV', 'Wave limit (Hs) (m)'].values[0]
ctv_precipitation = df_transport_data.loc[df_transport_data['Transport'] == 'CTV', 'Precipitation'].values[0]
ctv_ice_coverage = df_transport_data.loc[df_transport_data['Transport'] == 'CTV','Ice'].values[0]


# Condiciones en las que un CTV puede trabajar

df['ctv_works'] = np.where((df['Visibility'] > ctv_visibility) &
                            (df['Wind_speed_150m'] < ctv_wind_speed_150m) &
                            (df['Sign._wave_height_(Hs)'] < ctv_sign_wave_height) &
                            (df['Precipitation'] <= 7.6) & # CTV -> Precipitation = Moderate between 2,5 and 7,6 mm/h
                            (df['Ice_coverage'] == ctv_ice_coverage) &
                             
                             # Variables comunes 
                            (df['date'].dt.weekday < 5) & # Días laborales de la semana
                            (df['Hour'] >= 6) & (df['Hour'] <= 18) & # Entre las 06:00 y las 18:00
                            (df['Short_radiation'] > 0 ) & # Durante las horas de luz del día
                            (df['Temperature_80m'] > 0), 1,0) # Temperatura por encima de 0º centígrados


# ------------------------------ SOV -------------------------------------------------

# Criterios trabajo transportes

sov_visibility = df_transport_data.loc[df_transport_data['Transport'] == 'SOV','Visibility (km)'].values[0]
sov_wind_speed_150m = df_transport_data.loc[df_transport_data['Transport'] == 'SOV','Wind Limit to Work (technicians) (m/s)'].values[0]
sov_sign_wave_height = df_transport_data.loc[df_transport_data['Transport'] == 'SOV', 'Wave limit (Hs) (m)'].values[0]
sov_precipitation = df_transport_data.loc[df_transport_data['Transport'] == 'SOV', 'Precipitation'].values[0]
sov_ice_coverage = df_transport_data.loc[df_transport_data['Transport'] == 'SOV', 'Ice'].values[0]


# Condiciones en las que un SOV puede trabajar

df['sov_works'] = np.where((df['Visibility'] > sov_visibility) &
                            (df['Wind_speed_150m'] < sov_wind_speed_150m) &
                            (df['Sign._wave_height_(Hs)'] < sov_sign_wave_height) &
                            (df['Precipitation'] <= 7.6) & # SOV -> Precipitation = Moderate between 2,5 and 7,6 mm/h
                            (df['Ice_coverage'] == sov_ice_coverage) &
                             
                             # Variables comunes 
                            (df['date'].dt.weekday < 5) & # Días laborales de la semana
                            (df['Hour'] >= 6) & (df['Hour'] <= 18) & # Entre las 06:00 y las 18:00
                            (df['Short_radiation'] > 0 ) & # Durante las horas de luz del día
                            (df['Temperature_80m'] > 0), 1,0) # Temperatura por encima de 0º centígrados


# ------------------------------ HELICOPTER -------------------------------------------

# Criterios trabajo transportes

heli_visibility = df_transport_data.loc[df_transport_data['Transport'] == 'Helicopter','Visibility (km)'].values[0]
heli_wind_speed_150m = df_transport_data.loc[df_transport_data['Transport'] == 'Helicopter','Wind Limit to Work (technicians) (m/s)'].values[0]
heli_sign_wave_height = df_transport_data.loc[df_transport_data['Transport'] == 'Helicopter', 'Wave limit (Hs) (m)'].values[0]
heli_precipitation = df_transport_data.loc[df_transport_data['Transport'] == 'Helicopter', 'Precipitation'].values[0]
heli_ice_coverage = df_transport_data.loc[df_transport_data['Transport'] == 'Helicopter', 'Ice'].values[0]


# Condiciones en las que un Helicopter puede trabajar

df['heli_works'] = np.where((df['Visibility'] > heli_visibility) &
                            (df['Wind_speed_150m'] < heli_wind_speed_150m) &
                            (df['Sign._wave_height_(Hs)'] < heli_sign_wave_height) &
                            (df['Precipitation'] <= 2.5) & # Helicopter -> Precipitation = Light less than 2,5 mm/h
                            (df['Ice_coverage'] == heli_ice_coverage) &
                             
                             # Variables comunes 
                            (df['date'].dt.weekday < 5) & # Días laborales de la semana
                            (df['Hour'] >= 6) & (df['Hour'] <= 18) & # Entre las 06:00 y las 18:00
                            (df['Short_radiation'] > 0 ) & # Durante las horas de luz del día
                            (df['Temperature_80m'] > 0), 1,0) # Temperatura por encima de 0º centígrados



# Agrupamos por día, año y localización
df_work = df.groupby([df['date'].dt.date, 'Year', 'Month', 'location']).agg({
    'ctv_works': 'sum',
    'sov_works': 'sum',
    'heli_works': 'sum',
    'wtg': 'max',
    'power_wtg': 'max',
    'load_factor': 'max',
    'energy_price': 'max',
    'lost_energy_price': 'max',
    'surplus_energy_price': 'max',
    'prod_target': 'max',
    'fr': 'max',
    'corrective': 'max',
    'go_window': 'max',
    'preventive': 'max',
    'lat_OSW': 'max',
    'lon_OSW': 'max',
    'lat_sea_port': 'max',
    'lon_sea_port': 'max',
    'lat_heli_port': 'max',
    'lon_heli_port': 'max',
    'ctv_day_cost' : 'max',
    'sov_day_cost' : 'max',
    'heli_day_cost' : 'max'
}).reset_index()


def haversine(lat1, lon1, lat2, lon2):
    
    # Radio de la Tierra en millas náuticas
    R = 3440.065
    
    # Convertir las coordenadas de grados a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Diferencia de latitudes y longitudes
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Fórmula del haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
       
    # Distancia en millas náuticas
    distance_nm = R * c
    
    return distance_nm


# Calcular la distancia al sea_port
df_work['distance_sea_port'] = df_work.apply(lambda row:
                                                haversine(row['lat_OSW'], row['lon_OSW'],
                                                row['lat_sea_port'], row['lon_sea_port']),
                                                axis=1)

# Calcular la distancia al heli_port
df_work['distance_heli_port'] = df_work.apply(lambda row:
                                                haversine(row['lat_OSW'], row['lon_OSW'],
                                                row['lat_heli_port'], row['lon_heli_port']),
                                                axis=1)


# Variables velocidades de cada vehículo

ctv_speed = df_transport_data.loc[df_transport_data['Transport'] == 'CTV', 'Speed (kts)'].values[0]
sov_speed = df_transport_data.loc[df_transport_data['Transport'] == 'SOV', 'Speed (kts)'].values[0]
heli_speed = df_transport_data.loc[df_transport_data['Transport'] == 'Helicopter', 'Speed (kts)'].values[0]

# Variables tiempos de transferencia del vehículo al molino en horas

ctv_transfer = df_transport_data.loc[df_transport_data['Transport'] == 'CTV', 'Transfer time (min)'].values[0] / 60
sov_transfer = df_transport_data.loc[df_transport_data['Transport'] == 'SOV', 'Transfer time (min)'].values[0] / 60
heli_transfer = df_transport_data.loc[df_transport_data['Transport'] == 'Helicopter', 'Transfer time (min)'].values[0] / 60


# Calculamos los tiempos de transporte, desembarco y embarco de cada vehículo

# ---------------------------- CTV ---------------------------------------------------------
df_work['ctv_transport_time'] = df_work.apply(lambda row:
                                            (((row['distance_sea_port'] / ctv_speed) * 2) + # *2 viaje de ida y vuelta
                                            ((ctv_transfer) * 2)), axis=1)

# ---------------------------- SOV ---------------------------------------------------------
# SOV (utilizaremos solo el tiempo de un viaje de puerto al parque porque viaja cada 15 días)
df_work['sov_transport_time'] = df_work.apply(lambda row:
                                            ((row['distance_sea_port'] / sov_speed)), axis=1) # No sumamos '_transfer', lo haremos más adelante

# ---------------------------- Helicopter---------------------------------------------------
df_work['heli_transport_time'] = df_work.apply(lambda row:
                                            (((row['distance_heli_port'] / heli_speed) * 4) + # 1 viaje de ida y vuelta para llevar a los técnicos al parque
                                            ((heli_transfer) * 2)), axis=1)                   # 1 viaje de ida y vuelta para recoger a los técnicos del parque


# ------------------------------ CTV ------------------------------ 

df_work['ctv_efec_work_time'] = np.where(
    df_work['ctv_works'] > (df_work['ctv_transport_time'] + df_work['go_window']),
    df_work['ctv_works'] - df_work['ctv_transport_time'],0)


# ------------------------------ SOV ------------------------------ 

# Crear las columnas 'sov_efec_work_time' y 'sov_osw' en df_day
df_work['sov_efec_work_time'] = df_work['sov_works'].astype(float)
df_work['sov_osw'] = np.nan

# Iterar sobre cada localización en el DataFrame
for location in df_work['location'].unique():
    
    # Filtrar los datos por la localización actual
    df_local = df_work[df_work['location'] == location].copy()
    
    # Obtener el tiempo de transporte y la go window correspondiente a la localización desde df_local
    sov_transport_time = df_local['sov_transport_time'].values[0]  # Usar la columna del DataFrame
    go_window_time = df_local['go_window'].values[0]  # Usar la columna del DataFrame

    # Obtener el tiempo de transbordo correspondiente a la localización
    sov_transfer_time = sov_transfer * 2  # Asumiendo que 'sov_transfer' está definido

    # Buscar el primer día del dataset
    current_date = df_local['date'].min()
    
    # Intervalos de tiempo: 1 día
    time_delta_1 = pd.Timedelta(days=1)
    
    while current_date <= df_local['date'].max():
        # Comprobar si el SOV puede viajar al parque eólico y descontar el tiempo de viaje si puede
        if df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'].values[0] > sov_transport_time:
            df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'] -= sov_transport_time
            df_local.loc[df_local['date'] == current_date, 'sov_osw'] = 1  # El SOV está en el parque eólico
            
            # Si el SOV ha llegado al parque eólico, avanzar 15 días
            for day in range(15):
                if current_date > df_local['date'].max():
                    break  # Salir si excedemos el rango de fechas
        
                # Comprobar si puede trabajar ese día
                if df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'].values[0] > go_window_time:
                    df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'] -= sov_transfer_time  # Descontamos el tiempo
                else:
                    df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'] = 0  # No puede trabajar
        
                df_local.loc[df_local['date'] == current_date, 'sov_osw'] = 1  # El SOV está en el parque eólico
        
                # Avanzar un día
                current_date += time_delta_1
                
            # Pasados los 15 días, comprobar si el SOV puede volver al puerto
            while current_date <= df_local['date'].max():
                
                # Si puede viajar, descontamos el tiempo de viaje
                if df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'].values[0] > sov_transport_time:
                    df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'] -= sov_transport_time
            
                    # Comprobar si puede trabajar ese día
                    if df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'].values[0] > go_window_time:
                        df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'] -= sov_transfer_time  # Descontamos el tiempo
                    else:
                        df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'] = 0  # No puede trabajar
                        
                    df_local.loc[df_local['date'] == current_date, 'sov_osw'] = 0  # El SOV está en el puerto
                    current_date += time_delta_1
                    break
                
                # Si no puede viajar comprobamos el siguiente día
                else:
                    # Comprobar si puede trabajar ese día
                    if df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'].values[0] > go_window_time:
                        df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'] -= sov_transfer_time  # Descontamos el tiempo
                    else:
                        df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'] = 0  # No puede trabajar
                        
                    df_local.loc[df_local['date'] == current_date, 'sov_osw'] = 1  # El SOV está en el parque eólico
                    current_date += time_delta_1

        else:  # Si el SOV no puede viajar al parque eólico
            df_local.loc[df_local['date'] == current_date, 'sov_efec_work_time'] = 0  # No puede trabajar
            df_local.loc[df_local['date'] == current_date, 'sov_osw'] = 0  # El SOV está en el puerto
            current_date += time_delta_1
            if current_date > df_local['date'].max():
                break  # Salir si excedemos el rango de fechas
    
    # Actualizar el DataFrame original df_day con los cambios realizados en df_local de cada localización
    df_work.update(df_local)
    

# ------------------------------ HELICOPTER ------------------------------ 

df_work['heli_efec_work_time'] = np.where(
    df_work['heli_works'] > (df_work['heli_transport_time'] + df_work['go_window']),
    df_work['heli_works'] - df_work['heli_transport_time'],0)


# Creamos la columna 'ener_prod_day_mw' para saber la energía que produce cada parque eólico al día
df_work['ener_prod_day_mw'] = df_work['wtg'] * df_work['power_wtg'] * df_work['load_factor'] * 24

# Creamos la columna 'fail_per_hour' para saber las horas de avería de cada molino cada hora
df_work['fail_per_hour'] = (df_work['preventive'] + (df_work['fr'] * df_work['corrective'])) / (365 * 24)

# Creamos las variables '_no_access_hours' con las horas que cada vehículo NO puede acceder al parque
df_work['ctv_no_access_hours'] = 24 - df_work['ctv_efec_work_time']
df_work['sov_no_access_hours'] = 24 - df_work['sov_efec_work_time']
df_work['heli_no_access_hours'] = 24 - df_work['heli_efec_work_time']

# Calculamos las horas de avería de cada molino por no poder acceder al parque
df_work['ctv_fail_hours_per_wtg'] = (df_work['fail_per_hour'] * df_work['ctv_no_access_hours'])
df_work['sov_fail_hours_per_wtg'] = (df_work['fail_per_hour'] * df_work['sov_no_access_hours'])                                           
df_work['heli_fail_hours_per_wtg'] = (df_work['fail_per_hour'] * df_work['heli_no_access_hours'])

# Calcular las horas de parada de todo el parque por no poder acceder a reparar las averías
df_work['ctv_lost_hours_total'] = (df_work['ctv_fail_hours_per_wtg'] * df_work['wtg'])
df_work['sov_lost_hours_total'] = (df_work['sov_fail_hours_per_wtg'] * df_work['wtg'])                                        
df_work['heli_lost_hours_total'] = (df_work['heli_fail_hours_per_wtg'] * df_work['wtg'])

# Calcular la energía producida al año de todo el parque teniendo en cuenta las horas de no poder acceder a reparar las averías
df_work['ctv_ener_prod_mw'] = df_work['wtg'] * df_work['power_wtg'] * df_work['load_factor'] * \
                                 (24 - df_work['ctv_fail_hours_per_wtg'])
df_work['sov_ener_prod_mw'] = df_work['wtg'] * df_work['power_wtg'] * df_work['load_factor'] * \
                                 (24 - df_work['sov_fail_hours_per_wtg'])                                         
df_work['heli_ener_prod_mw'] = df_work['wtg'] * df_work['power_wtg'] * df_work['load_factor'] * \
                                 (24 - df_work['heli_fail_hours_per_wtg'])

# Calcular el porcentaje de productividad al año en función de cada vehículo
df_work['ctv_ener_prod_perc'] = (df_work['ctv_ener_prod_mw'] / df_work['ener_prod_day_mw'])
df_work['sov_ener_prod_perc'] = (df_work['sov_ener_prod_mw'] / df_work['ener_prod_day_mw'])                                      
df_work['heli_ener_prod_perc'] = (df_work['heli_ener_prod_mw'] / df_work['ener_prod_day_mw'])


# Cálculo de las compensaciones o penalizaciones

# Creamos la columna '*_energy_year_result_eur' con los valores correspondientes para cada vehículo
df_work['ctv_ener_compensation_eur'] = np.where(
    df_work['ctv_ener_prod_perc'] > df_work['prod_target'],
    (df_work['ctv_ener_prod_perc'] - df_work['prod_target']) * df_work['surplus_energy_price'],
    ((df_work['ctv_ener_prod_perc'] - df_work['prod_target']) * 
         df_work['ctv_ener_prod_mw'] * df_work['lost_energy_price']))

df_work['sov_ener_compensation_eur'] = np.where(
    df_work['sov_ener_prod_perc'] > df_work['prod_target'],
    (df_work['sov_ener_prod_perc'] - df_work['prod_target']) * df_work['surplus_energy_price'],
    ((df_work['sov_ener_prod_perc'] - df_work['prod_target']) * 
         df_work['sov_ener_prod_mw'] * df_work['lost_energy_price']))

df_work['heli_ener_compensation_eur'] = np.where(
    df_work['heli_ener_prod_perc'] > df_work['prod_target'],
    (df_work['heli_ener_prod_perc'] - df_work['prod_target']) * df_work['surplus_energy_price'],
    ((df_work['heli_ener_prod_perc'] - df_work['prod_target']) * 
         df_work['heli_ener_prod_mw'] * df_work['lost_energy_price']))


# ----------------------- Target PD ---------------------------------------------------

# Variable para CTV 'ctv_target_pd'
df_work['ctv_target_pd'] = ((df_work['wtg'] * df_work['fr'] * df_work['corrective']) / \
                            (24 * (df_work['wtg'])) * \
                            (df_work['ctv_no_access_hours'] / \
                            (df_work['preventive'] + (df_work['fr'] * df_work['corrective']))))

# Variable para SOV 'sov_target_pd'
df_work['sov_target_pd'] = ((df_work['wtg'] * df_work['fr'] * df_work['corrective']) / \
                            (24 * (df_work['wtg'])) * \
                            (df_work['sov_no_access_hours'] / \
                            (df_work['preventive'] + (df_work['fr'] * df_work['corrective']))))

# Variable para Helicopter 'heli_target_pd'
df_work['heli_target_pd'] = ((df_work['wtg'] * df_work['fr'] * df_work['corrective']) / \
                            (24 * (df_work['wtg'])) * \
                            (df_work['heli_no_access_hours'] / \
                            (df_work['preventive'] + (df_work['fr'] * df_work['corrective']))))


# ----------------------- Target LGD ---------------------------------------------------

# Variable para CTV 'ctv_target_lgd'    

df_work['ctv_target_lgd'] = np.where(df_work['ctv_ener_compensation_eur'] > 0,
                                     abs((((df_work['ener_prod_day_mw'] - df_work['ctv_ener_prod_mw']) * \
                            df_work['energy_price'] * 1000) + df_work['ctv_day_cost']) / \
                            (df_work['ener_prod_day_mw'] * df_work['energy_price'] * 1000)),
                                     abs((((df_work['ener_prod_day_mw'] - df_work['ctv_ener_prod_mw']) * \
                            df_work['energy_price'] * 1000) + abs(df_work['ctv_ener_compensation_eur']) + \
                            df_work['ctv_day_cost']) / \
                            (df_work['ener_prod_day_mw'] * df_work['energy_price'] * 1000)))


# Variable para SOV 'sov_target_lgd'
df_work['sov_target_lgd'] = np.where(df_work['sov_ener_compensation_eur'] > 0,
                                     abs((((df_work['ener_prod_day_mw'] - df_work['sov_ener_prod_mw']) * \
                            df_work['energy_price'] * 1000) + df_work['sov_day_cost']) / \
                            (df_work['ener_prod_day_mw'] * df_work['energy_price'] * 1000)),
                                     abs((((df_work['ener_prod_day_mw'] - df_work['sov_ener_prod_mw']) * \
                            df_work['energy_price'] * 1000) + abs(df_work['sov_ener_compensation_eur']) + \
                            df_work['sov_day_cost']) / \
                            (df_work['ener_prod_day_mw'] * df_work['energy_price'] * 1000)))


# Variable para Helicopter 'heli_target_lgd'
df_work['heli_target_lgd'] = np.where(df_work['heli_ener_compensation_eur'] > 0,
                                     abs((((df_work['ener_prod_day_mw'] - df_work['heli_ener_prod_mw']) * \
                            df_work['energy_price'] * 1000) + df_work['heli_day_cost']) / \
                            (df_work['ener_prod_day_mw'] * df_work['energy_price'] * 1000)),
                                     abs((((df_work['ener_prod_day_mw'] - df_work['heli_ener_prod_mw']) * \
                            df_work['energy_price'] * 1000) + abs(df_work['heli_ener_compensation_eur']) + \
                            df_work['heli_day_cost']) / \
                            (df_work['ener_prod_day_mw'] * df_work['energy_price'] * 1000)))


# Vamos a crear 3 variables donde meteremos los datos que tenemos en el dataset df_transport_data con 
# las emisiones de cada vehículo por hora o por día

ctv_emissions = df_transport_data.loc[df_transport_data['Transport'] == 'CTV', 'Emissions CO2'].iloc[0]
ctv_emissions = int(ctv_emissions.split('kg')[0]) / 1000 # en toneladas
sov_emissions = df_transport_data.loc[df_transport_data['Transport'] == 'SOV', 'Emissions CO2'].iloc[0]
sov_emissions = int(sov_emissions.split('kg')[0]) / 1000 # en toneladas
heli_emissions = df_transport_data.loc[df_transport_data['Transport'] == 'Helicopter', 'Emissions CO2'].iloc[0]
heli_emissions = int(heli_emissions.split('kg')[0]) / 1000 # en toneladas


# ----------------------- Emisiones CO2 CTV --------------------------------------

df_work['ctv_emissions'] = df_work['ctv_works'] * ctv_emissions


# ----------------------- Emisiones CO2 SOV --------------------------------------

df_work['sov_emissions'] = np.nan

# Iterar sobre cada localización en el DataFrame
for location in df_work['location'].unique():
    
    # Filtrar los datos por la localización actual
    df_local = df_work[df_work['location'] == location].copy()
        
    # Buscar el primer día del dataset
    current_date = df_local['date'].min()
    
    # Intervalos de tiempo: 1 día
    time_delta_1 = pd.Timedelta(days=1)
    
    while current_date <= df_local['date'].max():
        # Comprobar si el SOV está en el parque eólico o en el puerto
        if df_local.loc[df_local['date'] == current_date, 'sov_osw'].values[0] == 1: # Si SOV está en el parque eólico
            df_local.loc[df_local['date'] == current_date, 'sov_emissions'] = sov_emissions  # Emisiones CO2 = 24 horas      
            
        else: # Si SOV está en el puerto
            if df_local.loc[df_local['date'] == current_date, 'sov_works'].values[0] == 0: # Si no puede trabajar ese día
                df_local.loc[df_local['date'] == current_date, 'sov_emissions'] = 0 # Emisiones CO2 = 0

            elif df_local.loc[df_local['date'] == current_date, 'sov_works'].values[0] > 0: # Si puede viajar ese día
                df_local.loc[df_local['date'] == current_date, 'sov_emissions'] = (sov_emissions / 2) # Emisiones CO2 = medio día

        current_date += time_delta_1
        if current_date > df_local['date'].max():
            break  # Salir si excedemos el rango de fechas      
    
    
    # Actualizar el DataFrame original df_emissions con los cambios realizados en df_local de cada localización
    df_work.update(df_local)
    

# ----------------------- Emisiones CO2 Helicopter --------------------------------------

# Creamos la variable 'heli_flight_time' para saber cuanto tiempo ha volado el helicóptero cada día
df_work['heli_flight_time'] = df_work['heli_works'] - df_work['heli_efec_work_time']

# Calculas las emisiones de CO2
df_work['heli_emissions'] = df_work['heli_flight_time'] * heli_emissions


def ejecutar_modelos(df):
    #5.CALIDAD Y CREACION DE VARIABLES
    ctv_pd_final_variables = ['ctv_works','sov_works','heli_works','wtg','power_wtg','load_factor','energy_price',
                          'lost_energy_price','surplus_energy_price','prod_target','fr','corrective',
                          'go_window','preventive','ctv_efec_work_time','ener_prod_day_mw','fail_per_hour',
                          'ctv_no_access_hours','sov_no_access_hours','heli_no_access_hours',
                          'ctv_fail_hours_per_wtg','sov_fail_hours_per_wtg','heli_fail_hours_per_wtg',
                          'ctv_lost_hours_total','sov_lost_hours_total','heli_lost_hours_total',
                          'ctv_ener_prod_mw','sov_ener_prod_mw','heli_ener_prod_mw']

    sov_pd_final_variables = ['sov_works','heli_works','wtg','power_wtg','load_factor','energy_price',
                          'lost_energy_price','surplus_energy_price','prod_target','fr','corrective',
                          'go_window','preventive','lat_OSW','sov_efec_work_time','ener_prod_day_mw',
                          'fail_per_hour','ctv_no_access_hours','sov_no_access_hours','heli_no_access_hours',
                          'ctv_fail_hours_per_wtg','sov_fail_hours_per_wtg','heli_fail_hours_per_wtg',
                          'ctv_lost_hours_total','sov_lost_hours_total','heli_lost_hours_total',
                          'ctv_ener_prod_mw','sov_ener_prod_mw','heli_ener_prod_mw']

    heli_pd_final_variables = ['heli_works','wtg','power_wtg','load_factor','energy_price','lost_energy_price',
                           'surplus_energy_price','prod_target','fr','corrective','go_window','preventive',
                           'lat_OSW','lon_OSW','heli_efec_work_time','heli_day_cost','ener_prod_day_mw',
                           'fail_per_hour','ctv_no_access_hours','sov_no_access_hours','heli_no_access_hours',
                           'ctv_fail_hours_per_wtg','sov_fail_hours_per_wtg','heli_fail_hours_per_wtg',
                           'ctv_lost_hours_total','sov_lost_hours_total','heli_lost_hours_total',
                           'ctv_ener_prod_mw','sov_ener_prod_mw']


    ctv_lgd_final_variables = ['ctv_works','sov_works','heli_works','wtg','power_wtg','load_factor',
                           'energy_price','lost_energy_price','surplus_energy_price','prod_target',
                           'fr','corrective','ctv_efec_work_time','heli_efec_work_time','ctv_fail_hours_per_wtg',
                           'sov_fail_hours_per_wtg','heli_fail_hours_per_wtg','ctv_lost_hours_total',
                           'sov_lost_hours_total','heli_lost_hours_total','ctv_ener_prod_mw','sov_ener_prod_mw',
                           'heli_ener_prod_mw','ctv_ener_prod_perc','sov_ener_prod_perc','heli_ener_prod_perc',
                           'ctv_ener_compensation_eur','sov_ener_compensation_eur','heli_ener_compensation_eur']

    sov_lgd_final_variables = ['sov_works','heli_works','wtg','power_wtg','load_factor','energy_price',
                           'lost_energy_price','surplus_energy_price','prod_target','fr','corrective',
                           'go_window','lon_heli_port','sov_efec_work_time','heli_no_access_hours',
                           'ctv_fail_hours_per_wtg','sov_fail_hours_per_wtg','heli_fail_hours_per_wtg',
                           'ctv_lost_hours_total','sov_lost_hours_total','heli_lost_hours_total',
                           'ctv_ener_prod_mw','sov_ener_prod_mw','heli_ener_prod_mw','ctv_ener_prod_perc',
                           'sov_ener_prod_perc','heli_ener_prod_perc','ctv_ener_compensation_eur',
                           'sov_ener_compensation_eur']

    heli_lgd_final_variables = ['sov_works','heli_works','wtg','power_wtg','load_factor','energy_price',
                            'lost_energy_price','surplus_energy_price','prod_target','fr','corrective',
                            'go_window','lat_sea_port','heli_efec_work_time','heli_day_cost','ener_prod_day_mw',
                            'fail_per_hour','ctv_no_access_hours','sov_no_access_hours','heli_no_access_hours',
                            'ctv_fail_hours_per_wtg','sov_fail_hours_per_wtg','heli_fail_hours_per_wtg',
                            'ctv_lost_hours_total','sov_lost_hours_total','heli_lost_hours_total',
                            'ctv_ener_prod_mw','sov_ener_prod_mw','heli_ener_prod_mw']

    x_ctv_pd = df_work[ctv_pd_final_variables].copy()
    x_ctv_lgd = df_work[ctv_lgd_final_variables].copy()

    x_sov_pd = df_work[sov_pd_final_variables].copy()
    x_sov_lgd = df_work[sov_lgd_final_variables].copy()

    x_heli_pd = df_work[heli_pd_final_variables].copy()
    x_heli_lgd = df_work[heli_lgd_final_variables].copy()


    #6.CARGA PIPES DE EJECUCIÓN
    with open(root_pipe_ejecution_ctv_pd, mode='rb') as file:
        pipe_ejecution_ctv_pd = pickle.load(file)

    with open(root_pipe_ejecution_sov_pd, mode='rb') as file:
        pipe_ejecution_sov_pd = pickle.load(file)

    with open(root_pipe_ejecution_heli_pd, mode='rb') as file:
        pipe_ejecution_heli_pd = pickle.load(file)


    with open(root_pipe_ejecution_ctv_lgd, mode='rb') as file:
        pipe_ejecution_ctv_lgd = pickle.load(file)

    with open(root_pipe_ejecution_sov_lgd, mode='rb') as file:
        pipe_ejecution_sov_lgd = pickle.load(file)

    with open(root_pipe_ejecution_heli_lgd, mode='rb') as file:
        pipe_ejecution_heli_lgd = pickle.load(file)


    #7.EJECUCION
    ctv_pd = pipe_ejecution_ctv_pd.predict(x_ctv_pd)
    ctv_lgd = pipe_ejecution_ctv_lgd.predict(x_ctv_lgd)

    sov_pd = pipe_ejecution_sov_pd.predict(x_sov_pd)
    sov_lgd = pipe_ejecution_sov_lgd.predict(x_sov_lgd)

    heli_pd = pipe_ejecution_heli_pd.predict(x_heli_pd)
    heli_lgd = pipe_ejecution_heli_lgd.predict(x_heli_lgd)


    #8.RESULTADO
    ctv_principal = x_ctv_pd['ener_prod_day_mw'] * x_ctv_pd['energy_price'] * 1000
    ctv_EL = pd.DataFrame({'principal':ctv_principal,
                            'ctv_pd':ctv_pd,
                            'ctv_lgd':ctv_lgd})
    ctv_EL['ctv_expec_lost'] = round(ctv_EL.ctv_pd * ctv_EL.principal * ctv_EL.ctv_lgd,2)

    sov_principal = x_sov_pd['ener_prod_day_mw'] * x_sov_pd['energy_price'] * 1000
    sov_EL = pd.DataFrame({'principal':sov_principal,
                            'sov_pd':sov_pd,
                            'sov_lgd':sov_lgd})
    sov_EL['sov_expec_lost'] = round(sov_EL.sov_pd * sov_EL.principal * sov_EL.sov_lgd,2)

    heli_principal = x_heli_pd['ener_prod_day_mw'] * x_heli_pd['energy_price'] * 1000
    heli_EL = pd.DataFrame({'principal':heli_principal,
                            'heli_pd':heli_pd,
                            'heli_lgd':heli_lgd})
    heli_EL['heli_expec_lost'] = round(heli_EL.heli_pd * heli_EL.principal * heli_EL.heli_lgd,2)
