import streamlit as st
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import io
from fpdf import FPDF

# Configuración
SHEET_NAME = "CurvaMadurez"

# Conectar con Google Sheets
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(credentials)
sheet = client.open(SHEET_NAME).sheet1

# Cargar datos
data = sheet.get_all_records()
if not data:
    st.title("Curva de Madurez")
    st.warning("La hoja está vacía. Por favor, carga datos en Google Sheets.")
    st.stop()

df = pd.DataFrame(data)

# Edición de datos
st.title("Curva de Madurez")
st.sidebar.header("Opciones")

st.subheader("Datos cargados")
edited_df = st.data_editor(df, num_rows="dynamic")

# Regresión lineal
if "origen" in edited_df.columns and "pendiente" in edited_df.columns:
    X = edited_df["origen"].values.reshape(-1, 1)
    y = edited_df["pendiente"].values

    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)

    a = model.coef_[0]
    b = model.intercept_
    r2 = r2_score(y, y_pred)

    # Gráfico
    fig = px.scatter(
        edited_df, x="origen", y="pendiente",
        title="Curva de Madurez", trendline="ols"
    )
    st.plotly_chart(fig)

    st.markdown(f"**Ecuación de la recta:** pendiente = {a:.2f} * origen + {b:.2f}")
    st.markdown(f"**R²:** {r2:.3f}")

else:
    st.error("El DataFrame debe contener las columnas 'origen' y 'pendiente'")
    st.stop()

# Título del informe
titulo_informe = st.text_input("Título del informe", "Informe Curva de Madurez")

# Función para generar PDF
def generar_pdf(edited_df, a, b, r2) -> bytes:
    pdf = FPDF()
    pdf.add_page()

    # Encabezado fijo
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "IoT Provoleta", align="R", ln=1)

    # Título cargado por usuario
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, titulo_informe, ln=1, align="C")

    # Resultados principales
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Ecuación de la recta:", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"pendiente = {a:.2f} * origen + {b:.2f}", ln=1)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Coeficiente de determinación R²:", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"{r2:.3f}", ln=1)

    # Tabla con datos
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Datos utilizados", ln=1)

    pdf.set_font("Arial", "B", 10)
    for col in edited_df.columns:
        pdf.cell(40, 10, str(col), 1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    for _, row in edited_df.iterrows():
        for col in edited_df.columns:
            pdf.cell(40, 10, str(row[col]), 1)
        pdf.ln()

    output = io.BytesIO()
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    output.write(pdf_bytes)
    return output.getvalue()


# Descarga de PDF
pdf_content = generar_pdf(edited_df, a, b, r2)
st.download_button(
    "⬇️ Descargar PDF",
    data=pdf_content,
    file_name="curva_madurez.pdf",
    mime="application/pdf",
    key="pdf"
)
