import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- Para PDF con Matplotlib (sin Chrome/kaleido) ---
import matplotlib
matplotlib.use("Agg")  # backend sin GUI, estable en servidores
import matplotlib.pyplot as plt

# --- Google Sheets ---
import gspread
from google.oauth2.service_account import Credentials

st.title("Calibración estimada hormigones - IoT Provoleta")

# Título personalizado para informe/hoja
custom_title = st.text_input("📌 Título del informe/archivo", "Informe de calibración")

st.markdown("""
Esta aplicación permite ingresar resultados de ensayos de resistencia a compresión y calcular 
la relación con la madurez (método de Nurse-Saul).
""")

# Entradas de temperatura
temp_lab = st.number_input("Temperatura de laboratorio (°C)", value=23.0, step=0.1)
temp_datum = st.number_input("Temperatura datum (°C)", value=-10.0, step=0.1)

st.markdown("""
Nota: Como temper
