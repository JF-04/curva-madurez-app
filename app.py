import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os

# Carpeta temporal en Streamlit Cloud
OUTPUT_DIR = "generated_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(page_title="Curva de Madurez", layout="centered")

# =====================
# Función generar PDF
# =====================
def generar_pdf(fig, data, titulo_informe):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    # Título fijo a la derecha
    elementos.append(Paragraph("<para alignment='right'><b>IoT Provoleta</b></para>", styles['Normal']))
    elementos.append(Spacer(1, 12))

    # Título personalizado
    if titulo_informe:
        elementos.append(Paragraph(f"<b>{titulo_informe}</b>", styles['Title']))
        elementos.append(Spacer(1, 12))

    # Tabla de parámetros clave
    ordenada = data["Ordenada al origen"].iloc[0]
    pendiente = data["Pendiente"].iloc[0]
    tabla = Table(
        [["<b>Ordenada al origen</b>", f"{ordenada:.4f}"],
         ["<b>Pendiente</b>", f"{pendiente:.4f}"]],
        colWidths=[150, 150],
        hAlign='LEFT'
    )
    tabla.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    elementos.append(tabla)
    elementos.append(Spacer(1, 20))

    # Insertar gráfico como imagen
    img_buffer = BytesIO()
    fig.write_image(img_buffer, format="png")
    img_buffer.seek(0)

    from reportlab.platypus import Image
    elementos.append(Image(img_buffer, width=400, height=300))

    doc.build(elementos)
    buffer.seek(0)
    return buffer

# =====================
# App
# =====================
st.title("Curva de Madurez")

# Título dinámico del informe
titulo_informe = st.text_input("Título del informe", "")

# Datos de ejemplo (reemplazar por datos de Google Sheets si aplica)
df = pd.DataFrame({
    "X": [1, 2, 3, 4, 5],
    "Y": [2, 4.1, 6, 7.9, 10.2],
})
df["Ordenada al origen"] = [1.5]
df["Pendiente"] = [2.05]

fig = px.scatter(df, x="X", y="Y", trendline="ols")

# Exportar Excel
excel_buffer = BytesIO()
df.to_excel(excel_buffer, index=False)
excel_buffer.seek(0)
excel_path = os.path.join(OUTPUT_DIR, "reporte.xlsx")
with open(excel_path, "wb") as f:
    f.write(excel_buffer.getvalue())

# Exportar PDF
pdf_buffer = generar_pdf(fig, df, titulo_informe)
pdf_path = os.path.join(OUTPUT_DIR, "reporte.pdf")
with open(pdf_path, "wb") as f:
    f.write(pdf_buffer.getvalue())

# Botones de descarga
st.download_button("⬇️ Descargar Excel", data=excel_buffer, file_name="reporte.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
st.download_button("⬇️ Descargar PDF", data=pdf_buffer, file_name="reporte.pdf", mime="application/pdf")

st.success("✅ Archivos generados y guardados en la carpeta interna de Streamlit.")
