import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ==============================
# Funciones auxiliares
# ==============================
def export_to_excel(df, ordenada_al_origen, pendiente, r2):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Datos", index=False)

        resultados = pd.DataFrame({
            "Métrica": ["Ordenada al origen", "Pendiente", "R²"],
            "Valor": [ordenada_al_origen, pendiente, r2]
        })
        resultados.to_excel(writer, sheet_name="Resultados", index=False)

    return output.getvalue()

def export_to_pdf(df, ordenada_al_origen, pendiente, r2, titulo):
    output = BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    width, height = letter

    # Logo / título fijo
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 40, height - 40, "IoT Provoleta")

    # Título ingresado por el usuario
    if titulo:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height - 80, titulo)

    # Resultados en negrita
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 120, f"Ordenada al origen: {ordenada_al_origen:.2f}")
    c.drawString(40, height - 140, f"Pendiente: {pendiente:.2f}")

    # R² normal
    c.setFont("Helvetica", 12)
    c.drawString(40, height - 160, f"R²: {r2:.4f}")

    # Tabla con datos
    textobject = c.beginText(40, height - 200)
    textobject.setFont("Helvetica", 10)
    for col in df.columns:
        textobject.textLine(col)
    textobject.textLine("-" * 20)
    for _, row in df.iterrows():
        textobject.textLine(" | ".join(map(str, row.values)))
    c.drawText(textobject)

    c.showPage()
    c.save()
    return output.getvalue()

# ==============================
# App principal
# ==============================
st.set_page_config(page_title="Curva de Madurez", layout="wide")

st.title("Curva de Madurez")

uploaded_file = st.file_uploader("📂 Cargar archivo CSV/Excel con datos", type=["csv", "xlsx"])

titulo_informe = st.text_input("Título del informe (opcional)")

if uploaded_file:
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Datos cargados")
    st.dataframe(df)

    if df.shape[1] >= 2:
        x = df.iloc[:, 0].values.reshape(-1, 1)
        y = df.iloc[:, 1].values

        model = LinearRegression()
        model.fit(x, y)

        pendiente = model.coef_[0]
        ordenada_al_origen = model.intercept_
        y_pred = model.predict(x)
        r2 = r2_score(y, y_pred)

        st.subheader("Resultados de la regresión")
        st.write(f"**Ordenada al origen:** {ordenada_al_origen:.2f}")
        st.write(f"**Pendiente:** {pendiente:.2f}")
        st.write(f"R²: {r2:.4f}")

        # Gráfico
        fig, ax = plt.subplots()
        ax.scatter(x, y, label="Datos")
        ax.plot(x, y_pred, color="red", label="Regresión")
        ax.set_xlabel(df.columns[0])
        ax.set_ylabel(df.columns[1])
        ax.legend()
        st.pyplot(fig)

        # Botones de descarga
        excel_data = export_to_excel(df, ordenada_al_origen, pendiente, r2)
        pdf_data = export_to_pdf(df, ordenada_al_origen, pendiente, r2, titulo_informe)

        st.download_button(
            "⬇️ Descargar Excel",
            data=excel_data,
            file_name="resultados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.download_button(
            "⬇️ Descargar PDF",
            data=pdf_data,
            file_name="resultados.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("⚠️ El archivo debe tener al menos dos columnas numéricas.")
else:
    st.info("📌 Cargá un archivo para comenzar.")
