import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

# Simulación de tus datos (reemplazá con lo que tengas en la app)
data = {
    "Etapa": ["Inicio", "Planificación", "Ejecución", "Cierre"],
    "Madurez": [1, 2, 3, 4]
}
df = pd.DataFrame(data)

st.title("Curva de Madurez")

st.dataframe(df)

# ===== Exportar a Excel =====
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

# ===== Exportar a PDF =====
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
