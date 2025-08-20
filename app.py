import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from sklearn.linear_model import LinearRegression
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# =========================
# Configuración
# =========================
st.set_page_config(page_title="Curva de Madurez", layout="wide")

# =========================
# Título fijo arriba a la derecha
# =========================
st.markdown(
    "<h3 style='text-align: right; color: gray;'>IoT Provoleta</h3>",
    unsafe_allow_html=True
)

st.title("Curva de Madurez")

# Campo para título personalizado del informe
titulo_informe = st.text_input("Título del Informe", value="Informe de Resultados")

# =========================
# Funciones auxiliares
# =========================
def generar_pdf(fig, resultados, titulo_informe):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Título fijo
    elements.append(Paragraph("<b>IoT Provoleta</b>", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Título editable
    elements.append(Paragraph(f"<b>{titulo_informe}</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Resultados: primero ordenada, luego pendiente (ambos en negrita)
    ordenada = resultados.get("Ordenada al origen", "N/A")
    pendiente = resultados.get("Pendiente", "N/A")
    elements.append(Paragraph(f"<b>Ordenada al origen:</b> {ordenada}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Pendiente:</b> {pendiente}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Tabla de resultados
    data = [[k, v] for k, v in resultados.items()]
    table = Table([["Métrica", "Valor"]] + data)
    table.setStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black)
    ])
    elements.append(table)
    elements.append(Spacer(1, 12))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# =========================
# Ejemplo de datos
# =========================
x = np.arange(1, 11)
y = 2 * x + 5 + np.random.normal(0, 2, 10)
df = pd.DataFrame({"X": x, "Y": y})

# Ajuste de regresión lineal
X = df[["X"]]
y_vals = df["Y"]
reg = LinearRegression().fit(X, y_vals)
pendiente = round(reg.coef_[0], 2)
ordenada = round(reg.intercept_, 2)

# Guardamos resultados
resultados = {
    "Ordenada al origen": ordenada,
    "Pendiente": pendiente
}

# Gráfico
fig = px.scatter(df, x="X", y="Y", trendline="ols", title="Curva de Madurez")

st.plotly_chart(fig, use_container_width=True)

# =========================
# Botones de descarga
# =========================
# Descargar Excel
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="Datos")
    pd.DataFrame([resultados]).to_excel(writer, index=False, sheet_name="Resultados")
excel_buffer.seek(0)

st.download_button(
    label="⬇️ Descargar Excel",
    data=excel_buffer,
    file_name="curva_madurez.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    key="excel_download"
)

# Descargar PDF
pdf_buffer = generar_pdf(fig, resultados, titulo_informe)
st.download_button(
    label="⬇️ Descargar PDF",
    data=pdf_buffer,
    file_name="curva_madurez.pdf",
    mime="application/pdf",
    key="pdf_download"
)
