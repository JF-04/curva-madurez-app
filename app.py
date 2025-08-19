import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

# ============================
# CONFIGURACIÓN GOOGLE SHEETS
# ============================
st.set_page_config(page_title="Curva de Madurez", layout="centered")

# Nombre de la hoja de Google Sheets
SHEET_NAME = "CurvaMadurez"

# Credenciales desde secrets.toml en Streamlit Cloud
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(credentials)

# ============================
# CARGA DE DATOS
# ============================
try:
    sheet = client.open(SHEET_NAME).sheet1
    data = sheet.get_all_records()

    if not data:
        st.warning("⚠️ La hoja está vacía. Por favor, carga datos en Google Sheets.")
        st.stop()

    df = pd.DataFrame(data)

except Exception as e:
    st.error(f"❌ Error al conectar con Google Sheets: {e}")
    st.stop()

# ============================
# INTERFAZ
# ============================
st.title("📊 Curva de Madurez")
st.dataframe(df)

# ============================
# EXPORTAR A EXCEL
# ============================
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="CurvaMadurez", index=False)

st.download_button(
    label="⬇️ Descargar Excel",
    data=excel_buffer.getvalue(),
    file_name="curva_madurez.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    key="download_excel"
)

# ============================
# EXPORTAR A PDF
# ============================
pdf_buffer = BytesIO()
doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
styles = getSampleStyleSheet()
elements = []

# Título
elements.append(Paragraph("Curva de Madurez", styles['Heading1']))

# Tabla
table_data = [df.columns.tolist()] + df.values.tolist()
table = Table(table_data)
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("GRID", (0, 0), (-1, -1), 1, colors.black),
]))
elements.append(table)

doc.build(elements)

st.download_button(
    label="⬇️ Descargar PDF",
    data=pdf_buffer.getvalue(),
    file_name="curva_madurez.pdf",
    mime="application/pdf",
    key="download_pdf"
)
