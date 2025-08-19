import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import io
import gspread
from google.oauth2.service_account import Credentials

# ==============================
# CONFIGURACIÓN GOOGLE SHEETS
# ==============================
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Cargar credenciales desde secrets de Streamlit
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPE)
client = gspread.authorize(creds)

# Abrir la hoja de Google Sheets
SHEET_NAME = "CurvaMadurez"
sheet = client.open(Calib provos Streamlit).sheet1

# ==============================
# FUNCIÓN PARA GENERAR PDF
# ==============================
def generar_pdf(fig, data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Título
    elements.append(Paragraph("Reporte de Curva de Madurez", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    # Insertar tabla de datos
    elements.append(Paragraph("Datos ingresados:", styles["Heading2"]))
    elements.append(Spacer(1, 6))
    for idx, row in data.iterrows():
        elements.append(Paragraph(f"{row['Etapa']}: {row['Valor']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Guardar gráfico temporal
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format="png")
    img_buffer.seek(0)
    elements.append(Image(img_buffer, width=400, height=300))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==============================
# APP STREAMLIT
# ==============================
st.title("📊 Curva de Madurez")

# Leer datos de la hoja
data = pd.DataFrame(sheet.get_all_records())

if data.empty:
    st.warning("La hoja está vacía. Por favor, carga datos en Google Sheets.")
else:
    # Editar datos
    edited_data = st.data_editor(data, num_rows="dynamic")

    # Gráfico
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(edited_data["Etapa"], edited_data["Valor"], marker="o", linestyle="-")
    ax.set_title("Curva de Madurez")
    ax.set_xlabel("Etapas")
    ax.set_ylabel("Valores")
    st.pyplot(fig)

    # Botón para generar PDF
    if st.button("📄 Descargar PDF"):
        pdf_file = generar_pdf(fig, edited_data)
        st.download_button(
            label="⬇️ Descargar Reporte",
            data=pdf_file,
            file_name="curva_madurez.pdf",
            mime="application/pdf"
        )

    # Guardar cambios en Google Sheets
    if st.button("💾 Guardar en Google Sheets"):
        sheet.clear()
        sheet.update([edited_data.columns.values.tolist()] + edited_data.values.tolist())
        st.success("✅ Datos actualizados en Google Sheets")
