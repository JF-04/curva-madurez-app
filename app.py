import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- Configuración ---
SHEET_NAME = "Curva de Madurez"

# --- Autenticación con Google ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

# --- Abrir hoja ---
sheet = client.open(SHEET_NAME).sheet1
data = sheet.get_all_records()

# --- Si la hoja está vacía, crear encabezados por defecto ---
if not data:
    default_headers = ["Fecha", "Indicador 1", "Indicador 2", "Indicador 3"]
    sheet.append_row(default_headers)
    data = []

# --- Mostrar título ---
st.title("Curva de Madurez")

# --- Mostrar datos existentes ---
if data:
    df = pd.DataFrame(data)
    st.subheader("📊 Datos actuales")
    st.dataframe(df)
else:
    st.warning("Todavía no hay registros debajo de los encabezados.")

# --- Formulario para agregar datos ---
st.subheader("➕ Agregar nuevo registro")
with st.form("add_record"):
    indicador1 = st.number_input("Indicador 1", min_value=0.0, step=0.1)
    indicador2 = st.number_input("Indicador 2", min_value=0.0, step=0.1)
    indicador3 = st.number_input("Indicador 3", min_value=0.0, step=0.1)
    submitted = st.form_submit_button("Guardar registro")

    if submitted:
        new_row = [datetime.today().strftime("%Y-%m-%d"), indicador1, indicador2, indicador3]
        sheet.append_row(new_row)
        st.success("✅ Registro agregado correctamente.")
        st.experimental_rerun()
