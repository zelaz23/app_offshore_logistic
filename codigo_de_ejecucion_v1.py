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
archivo = st.file_uploader('Select a csv file')

if archivo is not None:
    df = pd.read_csv(archivo)
    st.write(df)

else:
    st.write("Please upload a csv file to continue")


# -------------------- CRITERIOS TRABAJO VEHÍCULOS ------------------------------
# Quitamos este código porque estos datos los introduciremos a mano en la pantalla de la app
# base_path = path + '/01_Documentos/Criterios_trabajo_transportes.csv'
# df_transport_data = pd.read_csv(base_path, sep=';')


# -------------------- DATOS PARQUES EÓLICOS ------------------------------
# Quitamos este código porque estos datos los introduciremos a mano en la pantalla de la app
# base_path = path + '/01_Documentos/Criterios_parques_eolicos.csv'
# df_osw_data = pd.read_csv(base_path, sep=';')


#3.VARIABLES Y REGISTROS FINALES

# Botón para ejecutar el procesamiento
    if st.button("Procesar datos"):

        df['date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])

        # Muestra los datos con la nueva columna 'date'
        st.write("Datos procesados con la columna 'date':")
        st.write(df)

#df['date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])


#4.FUNCIONES DE SOPORTE

