import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
from sklearn.metrics import r2_score
from io import BytesIO
import xlsxwriter
from fpdf import FPDF
import os

# ==========================
# CONFIG
# ==========================
st.set_page_config(page_title="Curva de Madurez", layout="wide")
st.title("Curva de Madurez")

SHEET_NAME = "CurvaMadurez"

# ==========================
# GOOGLE SHEETS
# ==========================
try:
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
    )
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # Normalizar nombres de columnas
    df.columns = [c.strip().lower() for c in df.columns]

except Exception as e:
    st.error(f"No se pudo acceder a la hoja: {e}")
    df = pd.DataFrame()

# ==========================
# CARGA DE TÍTULO
# ==========================
titulo_informe = st.text_input("Título del informe", "Informe de Curva de Madurez")

# ==========================
# VISUALIZACIÓN
# ==========================
if not df.empty and "origen" in df.columns and "pendiente" in df.columns:
    fig = px.scatter(
        df,
        x="origen",
        y="pendiente",
        title="Curva de Madurez",
        trendline="ols"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Calcular R²
    if "pendiente" in df.columns and "origen" in df.columns:
        try:
            import statsmodels.api as sm
            X = df["origen"]
            y = df["pendiente"]
            X_const = sm.add_constant(X)
            model = sm.OLS(y, X_const).fit()
            r2 = model.rsquared
            st.metric("R²", f"{r2:.4f}")
        except Exception:
            st.warning("No se pudo calcular R²")

else:
    st.warning("La hoja no tiene las columnas requeridas: 'origen' y 'pendiente'")

# ==========================
# EXPORTAR EXCEL
# ==========================
def export_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Curva")
    return output.getvalue()

# ==========================
# EXPORTAR PDF
# ==========================
def export_pdf(df, titulo_informe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)

    # Encabezado
    pdf.cell(200, 10, "IoT Provoleta", ln=True, align="R")
    pdf.ln(5)

    # Título dinámico
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, titulo_informe, ln=True, align="C")
    pdf.ln(10)

    # Contenido tabla
    pdf.set_font("Arial", "B", 12)
    pdf.cell(90, 10, "Origen", 1, 0, "C")
    pdf.cell(90, 10, "Pendiente", 1, 1, "C")

    pdf.set_font("Arial", "", 12)
    for _, row in df.iterrows():
        pdf.cell(90, 10, str(row["origen"]), 1, 0, "C")
        pdf.cell(90, 10, str(row["pendiente"]), 1, 1, "C")

    return pdf.output(dest="S").encode("latin-1")

# ==========================
# BOTONES DE DESCARGA
# ==========================
if not df.empty:
    col1, col2 = st.columns(2)

    with col1:
        excel_data = export_excel(df)
        st.download_button(
            label="⬇️ Descargar Excel",
            data=excel_data,
            file_name="curva_madurez.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="excel"
        )

    with col2:
        pdf_data = export_pdf(df, titulo_informe)
        st.download_button(
            label="⬇️ Descargar PDF",
            data=pdf_data,
            file_name="curva_madurez.pdf",
            mime="application/pdf",
            key="pdf"
        )
