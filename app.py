import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from io import BytesIO
import zipfile
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

# ============================
# CONFIGURACIÓN GOOGLE SHEETS
# ============================
st.set_page_config(page_title="Curva de Madurez", layout="centered")

SHEET_NAME = "CurvaMadurez"

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
# SESIÓN DE ARCHIVOS
# ============================
if "files" not in st.session_state:
    st.session_state["files"] = []  # lista de tuplas (filename, content, mime)

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

excel_content = excel_buffer.getvalue()
excel_name = "curva_madurez.xlsx"

if st.download_button(
    label="⬇️ Descargar Excel",
    data=excel_content,
    file_name=excel_name,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    key="download_excel"
):
    st.session_state["files"].append((excel_name, excel_content,
                                      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))

# ============================
# EXPORTAR A PDF
# ============================
pdf_buffer = BytesIO()
doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
styles = getSampleStyleSheet()
elements = []

elements.append(Paragraph("Curva de Madurez", styles['Heading1']))
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
pdf_content = pdf_buffer.getvalue()
pdf_name = "curva_madurez.pdf"

if st.download_button(
    label="⬇️ Descargar PDF",
    data=pdf_content,
    file_name=pdf_name,
    mime="application/pdf",
    key="download_pdf"
):
    st.session_state["files"].append((pdf_name, pdf_content, "application/pdf"))

# ============================
# DESCARGAR TODOS JUNTOS (ZIP)
# ============================
if st.session_state["files"]:
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for fname, content, _ in st.session_state["files"]:
            zipf.writestr(fname, content)

    st.download_button(
        label="⬇️ Descargar todos (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="documentos_curva_madurez.zip",
        mime="application/zip",
        key="download_zip"
    )
