import streamlit as st
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from sklearn.linear_model import LinearRegression
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ======================
# CONFIGURACIÓN STREAMLIT
# ======================
st.set_page_config(page_title="Curva de Madurez", layout="wide")

# Título fijo y título editable
col1, col2 = st.columns([4,1])
with col1:
    informe_titulo = st.text_input("Título del informe:", "Curva de Madurez")
with col2:
    st.markdown("<h3 style='text-align: right;'>IoT Provoleta</h3>", unsafe_allow_html=True)

# ======================
# CONEXIÓN A GOOGLE SHEETS
# ======================
SHEET_NAME = "CurvaMadurez"

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)

try:
    sheet = client.open(SHEET_NAME).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
except Exception:
    st.error("⚠️ No se pudo acceder a la hoja. Verifica permisos o nombre.")
    st.stop()

if df.empty:
    st.warning("La hoja está vacía. Carga datos en Google Sheets.")
    st.stop()

# ======================
# ANÁLISIS DE REGRESIÓN
# ======================
X = df.iloc[:, 0].values.reshape(-1, 1)  # primera columna como X
y = df.iloc[:, 1].values                 # segunda columna como y

modelo = LinearRegression()
modelo.fit(X, y)

ordenada_al_origen = modelo.intercept_
pendiente = modelo.coef_[0]

# ======================
# MOSTRAR DATOS Y RESULTADOS
# ======================
st.subheader("Datos cargados")
st.dataframe(df)

st.subheader("Resultados de la regresión")
st.write(f"**Ordenada al origen:** {ordenada_al_origen:.2f}")
st.write(f"**Pendiente:** {pendiente:.2f}")

# ======================
# EXPORTAR A EXCEL
# ======================
def export_excel():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Datos")
        resultados = pd.DataFrame({
            "Métrica": ["Ordenada al origen", "Pendiente"],
            "Valor": [ordenada_al_origen, pendiente]
        })
        resultados.to_excel(writer, index=False, sheet_name="Resultados")
    return output.getvalue()

# ======================
# EXPORTAR A PDF
# ======================
def export_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Título
    story.append(Paragraph(f"<b>{informe_titulo}</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # Resultados primero
    story.append(Paragraph(f"<b>Ordenada al origen:</b> {ordenada_al_origen:.2f}", styles["Normal"]))
    story.append(Paragraph(f"<b>Pendiente:</b> {pendiente:.2f}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Datos de tabla en texto
    story.append(Paragraph("<b>Datos:</b>", styles["Heading2"]))
    for _, row in df.iterrows():
        story.append(Paragraph(str(row.to_dict()), styles["Normal"]))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# ======================
# BOTONES DE DESCARGA
# ======================
col1, col2 = st.columns(2)

with col1:
    st.download_button(
        "⬇️ Descargar Excel",
        data=export_excel(),
        file_name="curva_madurez.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    st.download_button(
        "⬇️ Descargar PDF",
        data=export_pdf(),
        file_name="curva_madurez.pdf",
        mime="application/pdf"
    )
