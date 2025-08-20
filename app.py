import streamlit as st
import pandas as pd
import plotly.express as px
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import os

# ---------------------------
# Configuración
# ---------------------------
st.set_page_config(page_title="Curva de Madurez", layout="wide")

# Carpeta donde se guardarán los archivos generados
OUTPUT_DIR = "generated_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------
# Interfaz
# ---------------------------
col1, col2 = st.columns([4, 1])
with col1:
    st.title("Curva de Madurez")
with col2:
    st.markdown("### IoT Provoleta")  # fijo arriba a la derecha

# Campo para título personalizado
titulo_informe = st.text_input("Ingrese un título para el informe:", "")

# Simulación de datos (puedes reemplazar por Google Sheets u otra fuente)
data = {
    "X": [1, 2, 3, 4, 5],
    "Y": [2, 4, 5, 4, 5]
}
df = pd.DataFrame(data)

# ---------------------------
# Gráfico
# ---------------------------
fig = px.scatter(df, x="X", y="Y", title="Curva de Madurez", trendline="ols")

# Extraer pendiente y ordenada
results = px.get_trendline_results(fig)
model = results.iloc[0]["px_fit_results"]
pendiente = model.params[1]
ordenada = model.params[0]

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Funciones de exportación
# ---------------------------
def generar_pdf(fig, data, titulo_informe, pendiente, ordenada, filename):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Agregar título personalizado si existe
    if titulo_informe:
        elements.append(Paragraph(f"<b>{titulo_informe}</b>", styles["Title"]))
        elements.append(Spacer(1, 12))

    # IoT Provoleta fijo arriba a la derecha
    elements.append(Paragraph("<para alignment='right'><b>IoT Provoleta</b></para>", styles["Normal"]))
    elements.append(Spacer(1, 24))

    # Texto análisis (primero ordenada, luego pendiente, ambos en negrita)
    elements.append(Paragraph(f"<b>Ordenada al origen:</b> {ordenada:.2f}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Pendiente:</b> {pendiente:.2f}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Tabla con datos
    table_data = [list(data.columns)] + data.values.tolist()
    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    # Guardar archivo
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(pdf)

    return pdf


def generar_excel(data, filename):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        data.to_excel(writer, index=False, sheet_name="Datos")
    excel_data = buffer.getvalue()

    # Guardar archivo
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(excel_data)

    return excel_data


# ---------------------------
# Botones de descarga
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("📄 Exportar PDF"):
        try:
            pdf_data = generar_pdf(fig, df, titulo_informe, pendiente, ordenada, "informe.pdf")
            st.download_button("⬇️ Descargar PDF", data=pdf_data, file_name="informe.pdf", mime="application/pdf", key="pdf_dl")
            st.success("✅ PDF generado y guardado en Streamlit Cloud")
        except Exception as e:
            st.error(f"⚠️ Error al exportar PDF: {e}")

with col2:
    if st.button("📊 Exportar Excel"):
        try:
            excel_data = generar_excel(df, "informe.xlsx")
            st.download_button("⬇️ Descargar Excel", data=excel_data, file_name="informe.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="excel_dl")
            st.success("✅ Excel generado y guardado en Streamlit Cloud")
        except Exception as e:
            st.error(f"⚠️ Error al exportar Excel: {e}")
