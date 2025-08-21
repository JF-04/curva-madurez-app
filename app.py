import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import io
from fpdf import FPDF

# =============================
# Configuración inicial
# =============================
st.set_page_config(page_title="Curva de Madurez", layout="wide")

# =============================
# Entrada de datos
# =============================
st.title("Curva de Madurez")

# Campo para ingresar el título del informe
titulo_informe = st.text_input("Ingrese un título para el informe:")

# Ejemplo de dataframe (reemplazar por Google Sheets o carga CSV)
data = pd.DataFrame({
    "X": [1, 2, 3, 4, 5],
    "Y": [2, 4, 5, 4, 5]
})

# =============================
# Gráfico
# =============================
fig = px.scatter(data, x="X", y="Y", trendline="ols", title="Curva de Madurez")
st.plotly_chart(fig, use_container_width=True)

# =============================
# Exportar PDF
# =============================
def generar_pdf(fig, data, titulo_informe):
    buffer = io.BytesIO()
    img_buffer = io.BytesIO()
    pio.write_image(fig, img_buffer, format="png")

    pdf = FPDF()
    pdf.add_page()

    # Título cargado por el usuario
    if titulo_informe:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, titulo_informe, ln=True, align="C")

    # Texto fijo IoT Provoleta arriba a la derecha
    pdf.set_font("Arial", 'I', 10)
    pdf.set_xy(-40, 10)
    pdf.cell(0, 10, "IoT Provoleta", align="R")

    # Gráfico
    pdf.image(img_buffer, x=10, y=30, w=180)

    # Cálculos de regresión
    results = px.get_trendline_results(fig)
    if not results.empty:
        model = results.iloc[0]["px_fit_results"]
        pendiente = model.params[1]
        ordenada = model.params[0]

        pdf.ln(95)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Ordenada al origen: {ordenada:.2f}", ln=True)
        pdf.cell(0, 10, f"Pendiente: {pendiente:.2f}", ln=True)

    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Botón de descarga PDF
if st.button("📄 Exportar a PDF"):
    try:
        pdf_file = generar_pdf(fig, data, titulo_informe)
        st.download_button("⬇️ Descargar informe PDF", data=pdf_file, file_name="curva_madurez.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"⚠️ Error al exportar PDF: {e}")
