#1.LIBRERIAS
import numpy as np
import pandas as pd
import pickle
import math
import streamlit as st
from datetime import datetime, time


#2.CARGA DATOS
'''
Cargamos los datos meteorológicos de todas las localizaciones, 
los criterios de trabajo de los vehículos y los datos de los 
parques eólicos que vamos a analizar
'''

# -------------------- DATOS METEOROLÓGICOS ------------------------------
'''
Estos datos los introduciremos cargando el archivo de datos meteorológicos en la pantalla de la app
'''


# -------------------- CRITERIOS TRABAJO VEHÍCULOS ------------------------------
'''
Estos datos los introduciremos a mano en la pantalla de la app
'''


# -------------------- DATOS PARQUES EÓLICOS ------------------------------
'''
Estos datos los introduciremos a mano en la pantalla de la app
'''

#3. PROCESAMIENTO DE DATOS
'''
Creamos la función "procesar_datos" para realizar todas las operaciones y cálculos necesarios sobre el dataframe
'''

def procesar_datos(df, local_data):
    # Creación la variable 'date' que incluya el día, mes y año
    df['date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])

    #4.FUNCIONES DE SOPORTE
    # Corrección de datos
    '''
    Cambiamos los puntos de los decimales por comas y convertimos a float
    todas las variables que hemos observado que no están correctamente identificadas
    '''
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
            
                    
    # ------- Meter los datos de local_data en el DataFrame df -------------------------

    # Asignar los valores al DataFrame correspondiente en la fila
    campos = ['lat_OSW','lon_OSW','lat_sea_port','lon_sea_port','lat_heli_port',
              'lon_heli_port','wtg','power_wtg','load_factor','energy_price',
              'lost_energy_price','surplus_energy_price','prod_target','principal',
              'fr','corrective','go_window','preventive','ctv_speed','sov_speed',
              'heli_speed','ctv_transfer','sov_transfer','heli_transfer','ctv_emissions',
              'sov_emissions','heli_emissions','ctv_day_cost','sov_day_cost','heli_day_cost']
    for campo in campos:
        df[campo] = local_data[campo].values[0]
            

    # ------------------------------ CRITERIOS DE TRABAJO GENERALES ----------------------

    working_days_str = local_data['working_days'].values[0]
    working_days_list = [day.strip() for day in working_days_str.split(",")]
    working_days_to_num = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
    working_days = [working_days_to_num[day] for day in working_days_list]
    working_hours_start_time = local_data['working_hours_start'].values[0]
    working_hours_start = working_hours_start_time.hour
    working_hours_end_time = local_data['working_hours_end'].values[0]
    working_hours_end = working_hours_end_time.hour
    temperature = local_data['temperature'].values[0]
    df['Hour'] = df['Hour'].apply(lambda x: x.hour if isinstance(x, time) else x)
        
        
    # ------------------------------ CTV -------------------------------------------------
    # Condiciones en las que un CTV puede trabajar
    df['ctv_works'] = np.where((df['Visibility'] > local_data['ctv_visibility'].iloc[0]) &
                                (df['Wind_speed_150m'] < local_data['ctv_wind_speed_150m'].iloc[0]) &
                                (df['Sign._wave_height_(Hs)'] < local_data['ctv_sign_wave_height'].iloc[0]) &
                                (df['Precipitation'] <= local_data['ctv_precipitation'].iloc[0]) & 
                                (df['Ice_coverage'] == local_data['ctv_ice_coverage'].iloc[0]) &

                                 # Variables comunes 
                                (df['date'].dt.weekday.isin(working_days)) &
                                (df['Hour'] >= working_hours_start) & (df['Hour'] <= working_hours_end) & 
                                (df['Short_radiation'] > 0 ) & # Durante las horas de luz del día
                                (df['Temperature_80m'] > temperature), 1,0)

    
    # ------------------------------ SOV -------------------------------------------------
    # Condiciones en las que un SOV puede trabajar
    df['sov_works'] = np.where((df['Visibility'] > local_data['sov_visibility'].iloc[0]) &
                                (df['Wind_speed_150m'] < local_data['sov_wind_speed_150m'].iloc[0]) &
                                (df['Sign._wave_height_(Hs)'] < local_data['sov_sign_wave_height'].iloc[0]) &
                                (df['Precipitation'] <= local_data['sov_precipitation'].iloc[0]) & 
                                (df['Ice_coverage'] == local_data['sov_ice_coverage'].iloc[0]) &

                                 # Variables comunes 
                                (df['date'].dt.weekday.isin(working_days)) & 
                                (df['Hour'] >= working_hours_start) & (df['Hour'] <= working_hours_end) &
                                (df['Short_radiation'] > 0 ) & # Durante las horas de luz del día
                                (df['Temperature_80m'] > temperature), 1,0)
    

    # ------------------------------ HELICOPTER -------------------------------------------
    # Condiciones en las que un Helicopter puede trabajar
    df['heli_works'] = np.where((df['Visibility'] > local_data['heli_visibility'].iloc[0]) &
                                (df['Wind_speed_150m'] < local_data['heli_wind_speed_150m'].iloc[0]) &
                                (df['Sign._wave_height_(Hs)'] < local_data['heli_sign_wave_height'].iloc[0]) &
                                (df['Precipitation'] <= local_data['heli_precipitation'].iloc[0]) & 
                                (df['Ice_coverage'] == local_data['heli_ice_coverage'].iloc[0]) &

                                 # Variables comunes 
                                (df['date'].dt.weekday.isin(working_days)) & 
                                (df['Hour'] >= working_hours_start) & (df['Hour'] <= working_hours_end) &
                                (df['Short_radiation'] > 0 ) & # Durante las horas de luz del día
                                (df['Temperature_80m'] > temperature), 1,0)
    
    # Agrupamos por día, año y localización
    df_work = df.groupby([df['date'].dt.date, 'Year', 'Month']).agg({
        'ctv_works': 'sum', 'sov_works': 'sum', 'heli_works': 'sum',
        'wtg': 'max', 'power_wtg': 'max', 'load_factor': 'max',
        'energy_price': 'max', 'lost_energy_price': 'max',
        'surplus_energy_price': 'max', 'prod_target': 'max',
        'fr': 'max', 'corrective': 'max', 'go_window': 'max',
        'preventive': 'max', 'lat_OSW': 'max', 'lon_OSW': 'max',
        'lat_sea_port': 'max', 'lon_sea_port': 'max', 'lat_heli_port': 'max',
        'lon_heli_port': 'max', 'ctv_day_cost' : 'max','sov_day_cost' : 'max',
        'heli_day_cost' : 'max'}).reset_index()

    # Función 'Haversine'
    '''
    Función 'Haversine' empleada para realizar el cálculo de 
    distancias desde los puertos a los parques eólicos
    '''
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

    # Cálculo de distancias desde los puertos a los parques eólicos
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
    
    # Cálculos de tiempos de viajes y transferencia de los vehículos a los molinos
    # Variables tiempos de transferencia del vehículo al molino en horas
    ctv_transfer = local_data['ctv_transfer'].values[0] / 60
    sov_transfer = local_data['sov_transfer'].values[0] / 60
    heli_transfer = local_data['heli_transfer'].values[0] / 60

    # Calculamos los tiempos de transporte, desembarco y embarco de cada vehículo
    # ---------------------------- CTV ---------------------------------------------------------
    df_work['ctv_transport_time'] = df_work.apply(lambda row:
                                                (((row['distance_sea_port'] / local_data['ctv_speed']) * 2) + # *2 viaje de ida y vuelta
                                                ((ctv_transfer) * 2)), axis=1)
    # ---------------------------- SOV ---------------------------------------------------------
    # SOV (utilizaremos solo el tiempo de un viaje de puerto al parque porque viaja cada 15 días)
    df_work['sov_transport_time'] = df_work.apply(lambda row:
                                                ((row['distance_sea_port'] / local_data['sov_speed'])), axis=1) # No sumamos '_transfer', lo haremos más adelante
    # ---------------------------- Helicopter---------------------------------------------------
    df_work['heli_transport_time'] = df_work.apply(lambda row:
                                                (((row['distance_heli_port'] / local_data['heli_speed']) * 3) + # 1 viaje de ida para llevar a los técnicos al parque
                                                ((heli_transfer) * 2)), axis=1)                                 # 1 viaje de ida y vuelta para recoger a los técnicos del parque


    # Cálculo del tiempo efectivo de trabajo de cada vehículo
    # ------------------------------ CTV ------------------------------ 
    df_work['ctv_effec_work_time'] = np.where(
        df_work['ctv_works'] > (df_work['ctv_transport_time'] + df_work['go_window']),
        df_work['ctv_works'] - df_work['ctv_transport_time'],0)

    # ------------------------------ SOV ------------------------------ 
    # Crear las columnas 'sov_efec_work_time' y 'sov_osw' en df_day
    df_work['sov_effec_work_time'] = df_work['sov_works'].astype(float)
    df_work['sov_osw'] = np.nan

    # Obtener el tiempo de transporte y la go window correspondiente a la localización desde df_local
    sov_transport_time = df_work['sov_transport_time'].values[0] 
    go_window_time = df_work['go_window'].values[0] 
    # Obtener el tiempo de transbordo correspondiente a la localización
    sov_transfer_time = sov_transfer * 2 

    # Buscar el primer día del dataset
    current_date = df_work['date'].min()

    # Intervalos de tiempo: 1 día
    time_delta_1 = pd.Timedelta(days=1)

    while current_date <= df_work['date'].max():
        # Comprobar si el SOV puede viajar al parque eólico y descontar el tiempo de viaje si puede
        if df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'].values[0] > sov_transport_time:
            df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'] -= sov_transport_time
            df_work.loc[df_work['date'] == current_date, 'sov_osw'] = 1  # El SOV está en el parque eólico

            # Si el SOV ha llegado al parque eólico, avanzar 15 días
            for day in range(15):
                if current_date > df_work['date'].max():
                    break  # Salir si excedemos el rango de fechas

                # Comprobar si puede trabajar ese día
                if df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'].values[0] > go_window_time:
                    df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'] -= sov_transfer_time  # Descontamos el tiempo
                else:
                    df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'] = 0  # No puede trabajar

                df_work.loc[df_work['date'] == current_date, 'sov_osw'] = 1  # El SOV está en el parque eólico

                # Avanzar un día
                current_date += time_delta_1

            # Pasados los 15 días, comprobar si el SOV puede volver al puerto
            while current_date <= df_work['date'].max():

                # Si puede viajar, descontamos el tiempo de viaje
                if df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'].values[0] > sov_transport_time:
                    df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'] -= sov_transport_time

                    # Comprobar si puede trabajar ese día
                    if df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'].values[0] > go_window_time:
                        df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'] -= sov_transfer_time  # Descontamos el tiempo
                    else:
                        df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'] = 0  # No puede trabajar

                    df_work.loc[df_work['date'] == current_date, 'sov_osw'] = 0  # El SOV está en el puerto
                    current_date += time_delta_1
                    break

                # Si no puede viajar comprobamos el siguiente día
                else:
                    # Comprobar si puede trabajar ese día
                    if df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'].values[0] > go_window_time:
                        df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'] -= sov_transfer_time  # Descontamos el tiempo
                    else:
                        df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'] = 0  # No puede trabajar

                    df_work.loc[df_work['date'] == current_date, 'sov_osw'] = 1  # El SOV está en el parque eólico
                    current_date += time_delta_1

        else:  # Si el SOV no puede viajar al parque eólico
            df_work.loc[df_work['date'] == current_date, 'sov_effec_work_time'] = 0  # No puede trabajar
            df_work.loc[df_work['date'] == current_date, 'sov_osw'] = 0  # El SOV está en el puerto
            current_date += time_delta_1
            if current_date > df_work['date'].max():
                break  # Salir si excedemos el rango de fechas

    # ------------------------------ HELICOPTER ------------------------------ 
    df_work['heli_effec_work_time'] = np.where(
        df_work['heli_works'] > (df_work['heli_transport_time'] + df_work['go_window']),
        df_work['heli_works'] - df_work['heli_transport_time'],0)

    
    # Estimación de horas de fallo de los molinos y tiempo que estarán parados
    # Creamos la columna 'ener_prod_day_mw' para saber la energía que produce cada parque eólico al día
    df_work['ener_prod_day_mw'] = df_work['wtg'] * df_work['power_wtg'] * df_work['load_factor'] * 24

    # Creamos la columna 'fail_per_hour' para saber las horas de avería de cada molino cada hora
    df_work['fail_per_hour'] = (df_work['preventive'] + (df_work['fr'] * df_work['corrective'])) / (365 * 24)

    # Creamos las variables '_no_access_hours' con las horas que cada vehículo NO puede acceder al parque
    df_work['ctv_no_access_hours'] = 24 - df_work['ctv_effec_work_time']
    df_work['sov_no_access_hours'] = 24 - df_work['sov_effec_work_time']
    df_work['heli_no_access_hours'] = 24 - df_work['heli_effec_work_time']

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
    
    # Creación de las target PD y LGD
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

    # Cálculo de emisiones de CO₂
    '''
    Vamos a crear 3 variables donde meteremos los datos que tenemos en el dataset df_transport_data con 
    las emisiones de cada vehículo por hora o por día
    '''
    ctv_emissions = local_data['ctv_emissions'].values[0] / 1000 # en toneladas
    sov_emissions = local_data['sov_emissions'].values[0] / 1000 # en toneladas
    heli_emissions = local_data['heli_emissions'].values[0] / 1000 # en toneladas

    # ----------------------- Emisiones CO2 CTV --------------------------------------
    df_work['ctv_emissions'] = df_work['ctv_works'] * ctv_emissions

    # ----------------------- Emisiones CO2 SOV --------------------------------------
    df_work['sov_emissions'] = np.nan

    # Buscar el primer día del dataset
    current_date = df_work['date'].min()

    # Intervalos de tiempo: 1 día
    time_delta_1 = pd.Timedelta(days=1)

    while current_date <= df_work['date'].max():
        # Comprobar si el SOV está en el parque eólico o en el puerto
        if df_work.loc[df_work['date'] == current_date, 'sov_osw'].values[0] == 1: # Si SOV está en el parque eólico
            df_work.loc[df_work['date'] == current_date, 'sov_emissions'] = sov_emissions  # Emisiones CO2 = 24 horas      

        else: # Si SOV está en el puerto
            if df_work.loc[df_work['date'] == current_date, 'sov_works'].values[0] == 0: # Si no puede trabajar ese día
                df_work.loc[df_work['date'] == current_date, 'sov_emissions'] = 0 # Emisiones CO2 = 0

            elif df_work.loc[df_work['date'] == current_date, 'sov_works'].values[0] > 0: # Si puede viajar ese día
                df_work.loc[df_work['date'] == current_date, 'sov_emissions'] = (sov_emissions / 2) # Emisiones CO2 = medio día

        current_date += time_delta_1
        if current_date > df_work['date'].max():
            break  # Salir si excedemos el rango de fechas      

    # ----------------------- Emisiones CO2 Helicopter --------------------------------------
    # Creamos la variable 'heli_flight_time' para saber cuanto tiempo ha volado el helicóptero cada día
    df_work['heli_flight_time'] = df_work['heli_works'] - df_work['heli_effec_work_time']

    # Calculas las emisiones de CO2
    df_work['heli_emissions'] = df_work['heli_flight_time'] * heli_emissions 
        
    #5.CALIDAD Y CREACION DE VARIABLES
    # Selección de variables para x
    ctv_pd_final_variables = ['ctv_works','sov_works','heli_works','wtg','power_wtg','load_factor','energy_price',
                              'lost_energy_price','surplus_energy_price','prod_target','fr','corrective',
                              'go_window','preventive','ctv_effec_work_time','ener_prod_day_mw','fail_per_hour',
                              'ctv_no_access_hours','sov_no_access_hours','heli_no_access_hours',
                              'ctv_fail_hours_per_wtg','sov_fail_hours_per_wtg','heli_fail_hours_per_wtg',
                              'ctv_lost_hours_total','sov_lost_hours_total','heli_lost_hours_total',
                              'ctv_ener_prod_mw','sov_ener_prod_mw','heli_ener_prod_mw']

    sov_pd_final_variables = ['sov_works','heli_works','wtg','power_wtg','load_factor','energy_price',
                              'lost_energy_price','surplus_energy_price','prod_target','fr','corrective',
                              'go_window','preventive','lat_OSW','sov_effec_work_time','ener_prod_day_mw',
                              'fail_per_hour','ctv_no_access_hours','sov_no_access_hours','heli_no_access_hours',
                              'ctv_fail_hours_per_wtg','sov_fail_hours_per_wtg','heli_fail_hours_per_wtg',
                              'ctv_lost_hours_total','sov_lost_hours_total','heli_lost_hours_total',
                              'ctv_ener_prod_mw','sov_ener_prod_mw','heli_ener_prod_mw']

    heli_pd_final_variables = ['heli_works','wtg','power_wtg','load_factor','energy_price','lost_energy_price',
                               'surplus_energy_price','prod_target','fr','corrective','go_window','preventive',
                               'lat_OSW','lon_OSW','heli_effec_work_time','heli_day_cost','ener_prod_day_mw',
                               'fail_per_hour','ctv_no_access_hours','sov_no_access_hours','heli_no_access_hours',
                               'ctv_fail_hours_per_wtg','sov_fail_hours_per_wtg','heli_fail_hours_per_wtg',
                               'ctv_lost_hours_total','sov_lost_hours_total','heli_lost_hours_total',
                               'ctv_ener_prod_mw','sov_ener_prod_mw']


    ctv_lgd_final_variables = ['ctv_works','sov_works','heli_works','wtg','power_wtg','load_factor',
                               'energy_price','lost_energy_price','surplus_energy_price','prod_target',
                               'fr','corrective','ctv_effec_work_time','heli_effec_work_time','ctv_fail_hours_per_wtg',
                               'sov_fail_hours_per_wtg','heli_fail_hours_per_wtg','ctv_lost_hours_total',
                               'sov_lost_hours_total','heli_lost_hours_total','ctv_ener_prod_mw','sov_ener_prod_mw',
                               'heli_ener_prod_mw','ctv_ener_prod_perc','sov_ener_prod_perc','heli_ener_prod_perc',
                               'ctv_ener_compensation_eur','sov_ener_compensation_eur','heli_ener_compensation_eur']

    sov_lgd_final_variables = ['sov_works','heli_works','wtg','power_wtg','load_factor','energy_price',
                               'lost_energy_price','surplus_energy_price','prod_target','fr','corrective',
                               'go_window','lon_heli_port','sov_effec_work_time','heli_no_access_hours',
                               'ctv_fail_hours_per_wtg','sov_fail_hours_per_wtg','heli_fail_hours_per_wtg',
                               'ctv_lost_hours_total','sov_lost_hours_total','heli_lost_hours_total',
                               'ctv_ener_prod_mw','sov_ener_prod_mw','heli_ener_prod_mw','ctv_ener_prod_perc',
                               'sov_ener_prod_perc','heli_ener_prod_perc','ctv_ener_compensation_eur',
                               'sov_ener_compensation_eur']

    heli_lgd_final_variables = ['sov_works','heli_works','wtg','power_wtg','load_factor','energy_price',
                                'lost_energy_price','surplus_energy_price','prod_target','fr','corrective',
                                'go_window','lat_sea_port','heli_effec_work_time','heli_day_cost','ener_prod_day_mw',
                                'fail_per_hour','ctv_no_access_hours','sov_no_access_hours','heli_no_access_hours',
                                'ctv_fail_hours_per_wtg','sov_fail_hours_per_wtg','heli_fail_hours_per_wtg',
                                'ctv_lost_hours_total','sov_lost_hours_total','heli_lost_hours_total',
                                'ctv_ener_prod_mw','sov_ener_prod_mw','heli_ener_prod_mw']

    # Selección de x
    x_ctv_pd = df_work[ctv_pd_final_variables].copy()
    x_ctv_lgd = df_work[ctv_lgd_final_variables].copy()
    x_sov_pd = df_work[sov_pd_final_variables].copy()
    x_sov_lgd = df_work[sov_lgd_final_variables].copy()
    x_heli_pd = df_work[heli_pd_final_variables].copy()
    x_heli_lgd = df_work[heli_lgd_final_variables].copy()

    #6.CARGA PIPES DE EJECUCIÓN
    with open('pipe_ejecution_ctv_pd.pickle', mode='rb') as file:
        pipe_ejecution_ctv_pd = pickle.load(file)
    with open('pipe_ejecution_sov_pd.pickle', mode='rb') as file:
        pipe_ejecution_sov_pd = pickle.load(file)
    with open('pipe_ejecution_heli_pd.pickle', mode='rb') as file:
        pipe_ejecution_heli_pd = pickle.load(file)
    with open('pipe_ejecution_ctv_lgd.pickle', mode='rb') as file:
        pipe_ejecution_ctv_lgd = pickle.load(file)
    with open('pipe_ejecution_sov_lgd.pickle', mode='rb') as file:
        pipe_ejecution_sov_lgd = pickle.load(file)
    with open('pipe_ejecution_heli_lgd.pickle', mode='rb') as file:
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
    df_work['ctv_expec_lost'] = round(ctv_EL.ctv_pd * ctv_EL.principal * ctv_EL.ctv_lgd,2)

    sov_principal = x_sov_pd['ener_prod_day_mw'] * x_sov_pd['energy_price'] * 1000
    sov_EL = pd.DataFrame({'principal':sov_principal,
                            'sov_pd':sov_pd,
                            'sov_lgd':sov_lgd})
    df_work['sov_expec_lost'] = round(sov_EL.sov_pd * sov_EL.principal * sov_EL.sov_lgd,2)

    heli_principal = x_heli_pd['ener_prod_day_mw'] * x_heli_pd['energy_price'] * 1000
    heli_EL = pd.DataFrame({'principal':heli_principal,
                            'heli_pd':heli_pd,
                            'heli_lgd':heli_lgd})
    df_work['heli_expec_lost'] = round(heli_EL.heli_pd * heli_EL.principal * heli_EL.heli_lgd,2)    

    # Devuelve el DataFrame procesado
    return df_work


