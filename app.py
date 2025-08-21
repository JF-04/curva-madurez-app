import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from fpdf import FPDF
import io

# ==============================
# CONFIG
# ==============================
st.set_page_config(page_title="Curva de Madurez", layout="wide")

SHEET_NAME = "CurvaMadurez"

# ==============================
# CONEXIÓN GOOGLE SHEETS
# ==============================
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

try:
    sheet = client.open(SHEET_NAME).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"No se pudo acceder a la hoja: {e}")
    df = pd.DataFrame()

# ==============================
# TÍTULO Y SIDEBAR
# ==============================
st.title("Curva de Madurez")

# título editable para el informe
titulo_informe = st.text_input("📄 Título del informe", "Informe de Resultados")

# logo fijo arriba a la derecha (IoT Provoleta)
st.markdown(
    """
    <div style="position: absolute; top: 15px; right: 20px; font-weight: bold; font-size: 18px;">
        IoT Provoleta
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================
# GRÁFICO
# ==============================
if not df.empty:
    fig = px.scatter(df, x="origen", y="pendiente", title="Curva de Madurez", trendline="ols")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("La hoja está vacía. Por favor, carga datos en Google Sheets.")

# ==============================
# GENERAR PDF
# ==============================
def generar_pdf(titulo, datos):
    pdf = FPDF()
    pdf.add_page()

    # Título principal
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, titulo, ln=True, align="C")

    pdf.ln(10)

    # Tabla de datos
    pdf.set_font("Arial", "B", 12)
    pdf.cell(95, 10, "Origen", border=1, align="C")
    pdf.cell(95, 10, "Pendiente", border=1, align="C")
    pdf.ln()

    pdf.set_font("Arial", "", 12)
    for _, row in datos.iterrows():
        pdf.cell(95, 10, str(row["origen"]), border=1, align="C")
        pdf.cell(95, 10, str(row["pendiente"]), border=1, align="C")
        pdf.ln()

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# ==============================
# BOTONES DESCARGA
# ==============================
col1, col2 = st.columns(2)

with col1:
    if not df.empty:
        pdf_file = generar_pdf(titulo_informe, df)
        st.download_button(
            "⬇️ Descargar PDF",
            data=pdf_file,
            file_name="informe.pdf",
            mime="application/pdf",
            key="download_pdf"
        )

with col2:
    if not df.empty:
        excel_file = io.BytesIO()
        with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="CurvaMadurez")
        excel_file.seek(0)

        st.download_button(
            "⬇️ Descargar Excel",
            data=excel_file,
            file_name="informe.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel"
        )
