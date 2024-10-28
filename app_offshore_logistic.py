from codigo_de_ejecucion_v1 import *
import streamlit as st
from streamlit_echarts import st_echarts
from datetime import time
import pandas as pd


import streamlit as st

st.sidebar.button("CALCULATE BEST OPTION")




#CONFIGURACION DE LA PÁGINA
st.set_page_config(
     page_title = 'Offshore Wind Farm Logistic Analyzer',
     page_icon = 'image1.png',
     layout = 'wide')

#MAIN
st.title('OFFSHORE WIND FARM LOGISTIC ANALYZER')

""" #SIDEBAR
with st.sidebar:
    st.image('image4.png')

    #INPUTS DE LA APLICACION
    # Coordenadas de las ubicaciones
    location_osw_lat = st.number_input('OSW  Location lat', -90.000, 90.000, format="%.3f")
    location_osw_lon = st.number_input('OSW  Location lon', -180.000, 180.000, format="%.3f")
    location_sea_port_lat = st.number_input('Sea Port lat', -90.000, 90.000, format="%.3f")
    location_sea_port_lon = st.number_input('Sea Port lon', -180.000, 180.000, format="%.3f")
    location_heli_port_lat = st.number_input('Heli Port lat', -90.000, 90.000, format="%.3f")
    location_heli_port_lon = st.number_input('Heli Port lon', -180.000, 180.000, format="%.3f")
    
    # Datos de la instalación
    wtg = st.number_input('WTG installed', 1, 200)
    power = st.slider('Power/WTG (MW)', 1, 20)
    load = st.slider('Load Factor', 0.2, 0.8)
    price = st.slider('Energy price', 0.10, 0.50)
    lost_ener_price = st.slider('Lost energy price', 150, 500)
    surplus_ener_price = st.slider('Surplus energy price', 200000, 1000000)
    prod_target = st.slider('Productivity target', 0.80, 0.99)
    principal = wtg * power * load * price * 365 * 24 * 1000

    # Datos de mantenimiento
    fr = st.slider('Failure rate', 1.0, 5.0, step=0.5, format="%.1f")
    corrective = st.slider('Corrective mean time (hours)', 1, 10)
    go_window = st.slider('Go Window', 1, 5)
    preventive = st.slider('Preventive/WTG time per year (hours)', 100, 250)
    working_hours_start = st.time_input('Working hours - Start', time(6, 0))
    working_hours_end = st.time_input('Working hours - End', time(18, 0))
    working_days = st.multiselect('Working days', ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'])
    temperature = st.slider('Working temperature limit', -5, 60)

    #DATOS CONOCIDOS (fijadas como datos estaticos por simplicidad)
    ctv_visibility, sov_visibility, heli_visibility = 0.15, 2, 3
    ctv_wind, sov_wind, heli_wind = 20, 20, 20
    ctv_wave, sov_wave, heli_wave = 1.75, 3, 6
    ctv_precipitation, sov_precipitation, heli_precipitation = 7.6, 7.6, 2.5
    ctv_ice, sov_ice, heli_ice = 0, 0, 0
    ctv_speed, sov_speed, heli_speed = 20, 15, 140
    ctv_transfer, sov_transfer, heli_transfer = 30, 45, 15
    ctv_emissions, sov_emissions, heli_emissions = 938, 8040, 625
    ctv_cost, sov_cost, heli_cost = 6500, 35000, 10900



#CALCULAR

#Crear el registro

if st.sidebar.button('CALCULATE BEST OPTION'):
    st.write("Botón presionado. Creando registro...")  # Mensaje de verificación
    registro = pd.DataFrame({'location_osw_lat':[location_osw_lat],
                         'location_osw_lon':[location_osw_lon],
                         'location_sea_port_lat':[location_sea_port_lat],
                         'location_sea_port_lon':[location_sea_port_lon],
                         'location_heli_port_lat':[location_heli_port_lat],
                         'location_heli_port_lon':[location_heli_port_lon],
                         'wtg':[wtg],
                         'power':[power],
                         'load':[load],
                         'price':[price],
                         'lost_ener_price':[lost_ener_price],
                         'surplus_ener_price':[surplus_ener_price],
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
                         'ctv_wind':[ctv_wind],
                         'sov_wind':[sov_wind],
                         'heli_wind':[heli_wind],
                         'ctv_wave':[ctv_wave],
                         'sov_wave':[sov_wave],
                         'heli_wave':[heli_wave],
                         'ctv_precipitation':[ctv_precipitation],
                         'sov_precipitation':[sov_precipitation],
                         'heli_precipitation':[heli_precipitation],
                         'ctv_ice':[ctv_ice],
                         'sov_ice':[sov_ice],
                         'heli_ice':[heli_ice],
                         'ctv_speed':[ctv_speed],
                         'sov_speed':[sov_speed],
                         'heli_speed':[heli_speed],
                         'ctv_transfer':[ctv_transfer],
                         'sov_transfer':[sov_transfer],
                         'heli_transfer':[heli_transfer],
                         'heli_wind':[heli_wind],
                         'ctv_emissions':[ctv_emissions],
                         'sov_emissions':[sov_emissions],
                         'heli_emissions':[heli_emissions],
                         'ctv_cost':[ctv_cost],
                         'sov_cost':[sov_cost],
                         'heli_cost':[heli_cost],
                         })


    st.write("Registro creado con éxito:", registro)

 """
#CALCULAR RIESGO

# if st.sidebar.button('CALCULATE BEST OPTION'):

    """ 
    #Ejecutar el scoring
    ctv_EL = ejecutar_modelos(registro)
    sov_EL = ejecutar_modelos(registro)
    heli_EL = ejecutar_modelos(registro)

    #Calcular los kpis para CTV
    kpi_ctv_pd = int(ctv_EL.pd * 100)
    kpi_ctv_lgd = int(ctv_EL.lgd * 100)
    kpi_ctv_el = int(ctv_EL.principal * ctv_EL.pd * ctv_EL.lgd)

    #Calcular los kpis para SOV
    kpi_sov_pd = int(sov_EL.pd * 100)
    kpi_sov_lgd = int(sov_EL.lgd * 100)
    kpi_sov_el = int(sov_EL.principal * sov_EL.pd * sov_EL.lgd)

    #Calcular los kpis para Helicopter
    kpi_heli_pd = int(heli_EL.pd * 100)
    kpi_heli_lgd = int(heli_EL.lgd * 100)
    kpi_heli_el = int(heli_EL.principal * heli_EL.pd * heli_EL.lgd)

    #Velocimetros
    #Codigo de velocimetros tomado de https://towardsdatascience.com/5-streamlit-components-to-build-better-applications-71e0195c82d4
    #Velocimetro para CTV
    ctv_options = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
            "series": [
                {
                    "name": "Expected Lost",
                    "type": "gauge",
                    "axisLine": {
                        "lineStyle": {
                            "width": 10,
                        },
                    },
                    "progress": {"show": "true", "width": 10},
                    "detail": {"valueAnimation": "true", "formatter": "{value}"},
                    "data": [{"value": ctv_EL, "name": "PD"}],
                }
            ],
        }

    #Velocimetro para SOV
    sov_options = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
            "series": [
                {
                    "name": "Expected Lost",
                    "type": "gauge",
                    "axisLine": {
                        "lineStyle": {
                            "width": 10,
                        },
                    },
                    "progress": {"show": "true", "width": 10},
                    "detail": {"valueAnimation": "true", "formatter": "{value}"},
                    "data": [{"value": sov_EL, "name": "PD"}],
                }
            ],
        }

    #Velocimetro para Helicopter
    heli_options = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
            "series": [
                {
                    "name": "Expected Lost",
                    "type": "gauge",
                    "axisLine": {
                        "lineStyle": {
                            "width": 10,
                        },
                    },
                    "progress": {"show": "true", "width": 10,},
                    "detail": {"valueAnimation": "true", "formatter": "{value}"},
                    "data": [{"value": heli_EL, "name": "LGD"}],
                }
            ],
        }
    #Representarlos en la app
    col1,col2,col3 = st.columns(3)
    with col1:
        st_echarts(options=ctv_options, width="110%", key=0)
    with col2:
        st_echarts(options=sov_options, width="110%", key=1)
    with col3:
        st_echarts(options=heli_options, width="110%", key=2)

    #Prescripcion
    col1,col2,col3 = st.columns(3)
    with col1:
        st.write('Anual expected CO2 emissions:')
        st.metric(label="CO2 EMISSIONS", value = ctv_emissions)
    with col2:
        st.write('Anual expected CO2 emissions:')
        st.metric(label="CO2 EMISSIONS", value = sov_emissions)
    with col3:
        st.write('Anual expected CO2 emissions:')
        st.metric(label="CO2 EMISSIONS", value = heli_emissions) """

""" else:
    st.write('DEFINE THE PARAMETERS TO ANALIZE AND CLIC IN CALCULATE') """
