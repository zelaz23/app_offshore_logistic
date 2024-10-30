from codigo_de_ejecucion import *
import streamlit as st
from streamlit_echarts import st_echarts
from datetime import time
import pandas as pd
#import os
from PIL import Image


#CONFIGURACION DE LA PÁGINA
st.set_page_config(
     page_title = 'Offshore Wind Farm Logistic Analyzer',
     page_icon = 'image1.png',
     layout = 'wide')

#MAIN
#st.title('OFFSHORE WIND FARM LOGISTIC ANALYZER')
st.markdown(
    "<h1 style='text-align: center;'>OFFSHORE WIND FARM LOGISTIC ANALYZER</h1>",
    unsafe_allow_html=True)

#SIDEBAR
with st.sidebar:
    st.image('image4.png')

    # Cargar archivo CSV con los datos meteorologicos de la zona a analizar
    uploaded_file = st.file_uploader("Upload meteorologic data", type="csv", key="file_upload")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, sep=';')
        st.write("File uploaded succesfully")

    #INPUTS DE LA APLICACION
    # Coordenadas de las ubicaciones
    # lat_OSW: Lista de valores predefinidos con nombres
    lat_OSW_options = {
        "Bay of Biscay": 46.875,
        "North sea": 53.041,
        "Baltic sea": 54.834,
        "Taiwan": 24.749,
        "Other": None}

    # Desplegable de opciones
    selected_option_lat_OSW = st.selectbox('Select a latitude or type one:', options=list(lat_OSW_options.keys()))

    # Determina el valor de latitud según la opción seleccionada
    if "Other" in selected_option_lat_OSW:
        # Si selecciona "Other", habilitar el número manual
        lat_OSW = st.number_input('Type latitude:', min_value=-90.000, max_value=90.000, format="%.3f", value=0.000)
    else:
        # Si selecciona una opción predefinida, extraer el valor numérico
        lat_OSW = float(selected_option_lat_OSW.split(": ")[1])









    # Número de latitud basado en la selección
    if lat_OSW_options[selected_option] is not None:
        lat_OSW = lat_OSW_options[selected_option]
    else:
        lat_OSW = st.number_input('OSW Location lon, type one', -90.000, 90.000, format="%.3f")
    
    # lon_OSW: Lista de valores predefinidos con nombres
    lon_OSW_options = {
        "Bay of Biscay": -2.514,
        "North sea": 2.934,
        "Baltic sea": 14.068,
        "Taiwan": 120.802,
        "Other": None}

    # Desplegable de opciones
    selected_option = st.selectbox('Select a longitude or type one:', options=list(lon_OSW_options.keys()))

    # Número de latitud basado en la selección
    if lon_OSW_options[selected_option] is not None:
        lon_OSW = lon_OSW_options[selected_option]
    else:
        lon_OSW = st.number_input('OSW Location lon, type one', -180.000, 180.000, format="%.3f")

    # lat_sea_port: Lista de valores predefinidos con nombres
    lat_sea_port_options = {
        "Bay of Biscay": 46.725,
        "North sea": 52.578,
        "Baltic sea": 54.515,
        "Taiwan": 25.117,
        "Other": None}

    # Desplegable de opciones
    selected_option = st.selectbox('Select a latitude or type one:', options=list(lat_sea_port_options.keys()))

    # Número de latitud basado en la selección
    if lat_sea_port_options[selected_option] is not None:
        lat_sea_port = lat_sea_port_options[selected_option]
    else:
        lat_sea_port = st.number_input('Sea port location lat, type one', -90.000, 90.000, format="%.3f")

    # lon_sea_port: Lista de valores predefinidos con nombres
    lon_sea_port_options = {
        "Bay of Biscay": -2.350,
        "North sea": 1.738,
        "Baltic sea": 13.654,
        "Taiwan": 121.244,
        "Other": None}

    # Desplegable de opciones
    selected_option = st.selectbox('Select a longitude or type one:', options=list(lon_sea_port_options.keys()))

    # Número de latitud basado en la selección
    if lon_sea_port_options[selected_option] is not None:
        lon_sea_port = lon_sea_port_options[selected_option]
    else:
        lon_sea_port = st.number_input('Sea port location lon, type one', -180.000, 180.000, format="%.3f")

    # lat_heli_port: Lista de valores predefinidos con nombres
    lat_heli_port_options = {
        "Bay of Biscay": 46.725,
        "North sea": 52.635,
        "Baltic sea": 54.515,
        "Taiwan": 25.117,
        "Other": None}

    # Desplegable de opciones
    selected_option = st.selectbox('Select a latitude or type one:', options=list(lat_heli_port_options.keys()))

    # Número de latitud basado en la selección
    if lat_heli_port_options[selected_option] is not None:
        lat_heli_port = lat_heli_port_options[selected_option]
    else:
        lat_heli_port = st.number_input('Heli port location lat, type one', -90.000, 90.000, format="%.3f")

    # lon_heli_port: Lista de valores predefinidos con nombres
    lon_heli_port_options = {
        "Bay of Biscay": -2.350,
        "North sea": 1.726,
        "Baltic sea": 13.654,
        "Taiwan": 121.244,
        "Other": None}

    # Desplegable de opciones
    selected_option = st.selectbox('Select a longitude or type one:', options=list(lon_heli_port_options.keys()))

    # Número de latitud basado en la selección
    if lon_heli_port_options[selected_option] is not None:
        lon_heli_port = lon_heli_port_options[selected_option]
    else:
        lon_heli_port = st.number_input('Heli port location lon, type one', -180.000, 180.000, format="%.3f")
    
    # Datos de la instalacion
    wtg = st.number_input('WTG installed', 1, 200)
    power_wtg = st.slider('Power/WTG (MW)', 1, 20)
    load_factor = st.slider('Load Factor', 0.2, 0.8)
    energy_price = st.slider('Energy price', 0.10, 0.50)
    lost_energy_price = st.slider('Lost energy price', 150, 500)
    surplus_energy_price = st.slider('Surplus energy price', 200000, 600000)
    prod_target = st.slider('Productivity target', 0.80, 0.99)
    principal = wtg * power_wtg * load_factor * energy_price * 365 * 24 * 1000

    # Datos de mantenimiento
    fr = st.slider('Failure rate', 1.0, 5.0, step=0.5, format="%.1f")
    corrective = st.slider('Corrective mean time (hours)', 1, 10)
    go_window = st.slider('Go Window', 1, 5)
    preventive = st.slider('Preventive/WTG time per year (hours)', 100, 250)
    working_hours_start = st.time_input('Working hours - Start', time(6, 0))
    working_hours_end = st.time_input('Working hours - End', time(18, 0))
    working_days = st.multiselect('Working days', ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'])
    temperature = st.number_input('Working temperature limit', min_value=-5, max_value=30, value=0)

    #DATOS CONOCIDOS (fijadas como datos estaticos por simplicidad)
    ctv_visibility, sov_visibility, heli_visibility = 0.15, 2, 3
    ctv_wind_speed_150m, sov_wind_speed_150m, heli_wind_speed_150m = 20, 20, 20
    ctv_sign_wave_height, sov_sign_wave_height, heli_sign_wave_height = 1.75, 3, 6
    ctv_precipitation, sov_precipitation, heli_precipitation = 7.6, 7.6, 2.5
    ctv_ice_coverage, sov_ice_coverage, heli_ice_coverage = 0, 0, 0
    ctv_speed, sov_speed, heli_speed = 20, 15, 140
    ctv_transfer, sov_transfer, heli_transfer = 30, 45, 15
    ctv_emissions, sov_emissions, heli_emissions = 938, 8040, 625
    ctv_day_cost, sov_day_cost, heli_day_cost = 6500, 35000, 10900


#CALCULAR

#Crear el registro

if st.sidebar.button('CALCULATE BEST OPTION', key="calculate_option_button"):
    local_data = pd.DataFrame({'lat_OSW':[lat_OSW],
                         'lon_OSW':[lon_OSW],
                         'lat_sea_port':[lat_sea_port],
                         'lon_sea_port':[lon_sea_port],
                         'lat_heli_port':[lat_heli_port],
                         'lon_heli_port':[lon_heli_port],
                         'wtg':[wtg],
                         'power_wtg':[power_wtg],
                         'load_factor':[load_factor],
                         'energy_price':[energy_price],
                         'lost_energy_price':[lost_energy_price],
                         'surplus_energy_price':[surplus_energy_price],
                         'prod_target':[prod_target],
                         'principal':[principal],
                         'fr':[fr],
                         'corrective':[corrective],
                         'go_window':[go_window],
                         'preventive':[preventive],
                         'working_hours_start':[working_hours_start],
                         'working_hours_end':[working_hours_end],
                         'working_days':[", ".join(working_days)],
                         'temperature':[temperature],
                         'ctv_visibility':[ctv_visibility],
                         'sov_visibility':[sov_visibility],
                         'heli_visibility':[heli_visibility],
                         'ctv_wind_speed_150m':[ctv_wind_speed_150m],
                         'sov_wind_speed_150m':[sov_wind_speed_150m],
                         'heli_wind_speed_150m':[heli_wind_speed_150m],
                         'ctv_sign_wave_height':[ctv_sign_wave_height],
                         'sov_sign_wave_height':[sov_sign_wave_height],
                         'heli_sign_wave_height':[heli_sign_wave_height],
                         'ctv_precipitation':[ctv_precipitation],
                         'sov_precipitation':[sov_precipitation],
                         'heli_precipitation':[heli_precipitation],
                         'ctv_ice_coverage':[ctv_ice_coverage],
                         'sov_ice_coverage':[sov_ice_coverage],
                         'heli_ice_coverage':[heli_ice_coverage],
                         'ctv_speed':[ctv_speed],
                         'sov_speed':[sov_speed],
                         'heli_speed':[heli_speed],
                         'ctv_transfer':[ctv_transfer],
                         'sov_transfer':[sov_transfer],
                         'heli_transfer':[heli_transfer],
                         'ctv_emissions':[ctv_emissions],
                         'sov_emissions':[sov_emissions],
                         'heli_emissions':[heli_emissions],
                         'ctv_day_cost':[ctv_day_cost],
                         'sov_day_cost':[sov_day_cost],
                         'heli_day_cost':[heli_day_cost],
                         })

    #st.write("Data registered sucessfully --> Processing...", local_data)

    # Mensaje de verificación en caso de que no se cargue un archivo
    if uploaded_file is None:
        st.write("Please, upload meteorolgic data to continue")


#CALCULAR RIESGO

    #Ejecutar codigo_de_ejecucion
        # Procesar los datos cargados
    df_procesado = procesar_datos(df, local_data)
    df_procesado = df_procesado.groupby(['Year']).agg({
                'ctv_expec_lost': 'sum',
                'sov_expec_lost':'sum',
                'heli_expec_lost':'sum',
                'ctv_emissions': 'sum',
                'sov_emissions':'sum',
                'heli_emissions':'sum'
                }).reset_index()
    
    #st.write("Data after processing:", df_procesado)
    
    ctv_EL = df_procesado['ctv_expec_lost'].mean()
    sov_EL = df_procesado['sov_expec_lost'].mean()
    heli_EL = df_procesado['heli_expec_lost'].mean()

    ctv_EL = float(ctv_EL)
    sov_EL = float(sov_EL)
    heli_EL = float(heli_EL)

    # Asegurarse de que las expected lost son cadenas
    ctv_EL_str = str(ctv_EL) if isinstance(ctv_EL, (int, float)) else "N/A"
    sov_EL_str = str(sov_EL) if isinstance(sov_EL, (int, float)) else "N/A"
    heli_EL_str = str(heli_EL) if isinstance(heli_EL, (int, float)) else "N/A"
    ctv_EL_str = f"{round(ctv_EL):,}"
    sov_EL_str = f"{round(sov_EL):,}"
    heli_EL_str = f"{round(heli_EL):,}"
    
    ctv_emissions = df_procesado['ctv_emissions'].mean()
    sov_emissions = df_procesado['sov_emissions'].mean()
    heli_emissions = df_procesado['heli_emissions'].mean()

    ctv_emissions = float(ctv_emissions)
    sov_emissions = float(sov_emissions)
    heli_emissions = float(heli_emissions)

    # Asegurarse de que las emisiones de CO2 son cadenas
    ctv_emissions_str = str(ctv_emissions) if isinstance(ctv_emissions, (int, float)) else "N/A"
    sov_emissions_str = str(sov_emissions) if isinstance(sov_emissions, (int, float)) else "N/A"
    heli_emissions_str = str(heli_emissions) if isinstance(heli_emissions, (int, float)) else "N/A"
    ctv_emissions_str = f"{round(ctv_emissions):,}"
    sov_emissions_str = f"{round(sov_emissions):,}"
    heli_emissions_str = f"{round(heli_emissions):,}"

    #Velocimetros
    #Velocimetro para CTV
    ctv_options = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}M"},
            "title": {
            "text": ctv_EL_str + ' €',
            "left": "center",
            "top": "80%",  
            "textStyle": {"fontSize": 32, "fontWeight": "bold"}
            },
            "series": [
                {
                    "name": "Revenue",
                    "type": "gauge",
                    "min": 500,
                    "max": 2000,
                    "splitNumber": 5,
                    "axisLine": {"lineStyle": {"width": 10}},
                    "axisLabel": {"show": True, "distance": 5, "formatter": "{value}K",},
                    "progress": {"show": True, "width": 10},
                    "detail": {"show": False},
                    "data": [{"value": round(ctv_EL/1000), "name": "CTV"}],
                }
            ],
        }

    #Velocimetro para SOV
    sov_options = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}M"},
            "title": {
            "text": sov_EL_str + ' €',
            "left": "center",
            "top": "80%",  
            "textStyle": {"fontSize": 32, "fontWeight": "bold"}
            },
            "series": [
                {
                    "name": "Revenue",
                    "type": "gauge",
                    "min": 500,
                    "max": 2000,
                    "splitNumber": 5,
                    "axisLine": {"lineStyle": {"width": 10}},
                    "axisLabel": {"show": True, "distance": 5, "formatter": "{value}K",},
                    "progress": {"show": True, "width": 10},
                    "detail": {"show": False},
                    "data": [{"value": round(sov_EL/1000), "name": "SOV"}],
                }
            ],
        }

    #Velocimetro para Helicopter   
    heli_options = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}M"},
            "title": {
            "text": heli_EL_str + ' €',
            "left": "center",
            "top": "80%",  
            "textStyle": {"fontSize": 32, "fontWeight": "bold"}
            },
            "series": [
                {
                    "name": "Revenue",
                    "type": "gauge",
                    "min": 500,
                    "max": 2000,
                    "splitNumber": 5,
                    "axisLine": {"lineStyle": {"width": 10}},
                    "axisLabel": {"show": True, "distance": 5, "formatter": "{value}K",},
                    "progress": {"show": True, "width": 10},
                    "detail": {"show": False},
                    "data": [{"value": round(heli_EL/1000), "name": "Helicopter"}],
                }
            ],
        }


    #Representar los velocímetros en la app
    col1,col2,col3 = st.columns(3)
    with col1:
        st.image("r_image_ctv.png", width=400)
        st.markdown("<h3 style='text-align: center; font-size: 1.8em;'>Expected Loss for CTV</h3>", unsafe_allow_html=True)
        st_echarts(options=ctv_options, width="110%", key="ctv_gauge")
    with col2:
        st.image("r_image_sov_1.png", width=400)
        st.markdown("<h3 style='text-align: center; font-size: 1.8em;'>Expected Loss for SOV</h3>", unsafe_allow_html=True)
        st_echarts(options=sov_options, width="110%", key="sov_gauge")
    with col3:
        st.image("r_image_heli_2.png",  width=400)
        st.markdown("<h3 style='text-align: center; font-size: 1.8em;'>Expected Loss for Helicopter</h3>", unsafe_allow_html=True)
        st_echarts(options=heli_options, width="110%", key="heli_gauge")

    #Representar las emisiones de CO2 en la app
    col1,col2,col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div style="text-align: center;">
            <h3>CTV CO₂ Emissions</h3>
            <p style="font-size: 2em; font-weight: bold;">{ctv_emissions_str} ton</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style="text-align: center;">
            <h3>SOV CO₂ Emissions</h3>
            <p style="font-size: 2em; font-weight: bold;">{sov_emissions_str} ton</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style="text-align: center;">
            <h3>Helicopter CO₂ Emissions</h3>
            <p style="font-size: 2em; font-weight: bold;">{heli_emissions_str} ton</p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.write('UPLOAD METEOROLOGIC DATA, DEFINE THE PARAMETERS TO ANALIZE AND CLIC IN CALCULATE BEST OPTION')
