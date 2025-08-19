import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import numpy as np
from sklearn.metrics import r2_score
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Curva de Madurez", layout="wide")
st.title("Curva de Madurez")

# Alcances para Google Sheets
SCOPES = ["https://spreadsheets.google.com/feeds",
          "https://www.googleapis.com/auth/drive"]

# Cargar credenciales desde secrets
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

client = gspread.authorize(credentials)

# 👇 Pegar el ID de tu Google Sheet aquí
SHEET_ID = "1hjOyV_0gmJ8bGs2GsqrmL4hFIB2U_9N4iVbEwFfKJh4"
sheet = client.open_by_key(SHEET_ID).sheet1

# --- LECTURA DE DATOS ---
data = sheet.get_all_records()
if not data:
    st.warning("La hoja está vacía. Por favor, carga datos en Google Sheets.")
    st.stop()

df = pd.DataFrame(data)

# --- EDITOR DE DATOS ---
st.subheader("Datos experimentales")
edited_data = st.data_editor(df, num_rows="dynamic")

# --- AJUSTE CURVA ---
if "Madurez" not in edited_data.columns or "Resistencia" not in edited_data.columns:
    st.error("Tu hoja debe tener columnas llamadas 'Madurez' y 'Resistencia'.")
    st.stop()

x = edited_data["Madurez"].values
y = edited_data["Resistencia"].values

# Ajuste polinómico (grado 2)
coef = np.polyfit(x, y, 2)
poly_eq = np.poly1d(coef)

# Predicciones
x_line = np.linspace(min(x), max(x), 100)
y_line = poly_eq(x_line)

# R²
y_pred = poly_eq(x)
r2 = r2_score(y, y_pred)

# --- GRÁFICO ---
fig = px.scatter(edited_data, x="Madurez", y="Resistencia",
                 title=f"Curva de Madurez (R² = {r2:.3f})")

fig.add_traces(px.line(x=x_line, y=y_line).data)
fig.update_traces(hovertemplate="Madurez: %{x}<br>Resistencia: %{y}")
st.plotly_chart(fig, use_container_width=True)

# =====================================================
# EXPORTAR A EXCEL
# =====================================================
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    edited_data.to_excel(writer, sheet_name="Datos", index=False)

st.download_button(
    label="⬇️ Descargar Excel",
    data=excel_buffer.getvalue(),
    file_name="curva_madurez.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =====================================================
# EXPORTAR A PDF
# =====================================================
def generar_pdf(fig, data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Curva de Madurez", styles["Title"]))
    story.append(Spacer(1, 12))

    # Guardar gráfico como imagen en memoria
    img_bytes = fig.to_image(format="png")
    img_buffer = io.BytesIO(img_bytes)
    story.append(Image(img_buffer, width=400, height=300))
    story.append(Spacer(1, 12))

    # Tabla de datos
    table_data = [list(data.columns)] + data.values.tolist()
    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(table)

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

pdf_file = generar_pdf(fig, edited_data)

st.download_button(
    label="⬇️ Descargar PDF",
    data=pdf_file,
    file_name="curva_madurez.pdf",
    mime="application/pdf"
)
