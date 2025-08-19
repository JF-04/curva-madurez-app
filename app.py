import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials

st.title("Calibración estimada hormigones - IoT Provoleta")

# --- Inicializar almacenamiento de archivos en sesión ---
if "archivos_generados" not in st.session_state:
    st.session_state["archivos_generados"] = []

# ========================
# Entradas
# ========================
custom_title = st.text_input("📌 Título del informe/archivo", "Informe de calibración")
temp_lab = st.number_input("Temperatura de laboratorio (°C)", value=23.0, step=0.1)
temp_datum = st.number_input("Temperatura datum (°C)", value=-10.0, step=0.1)

st.subheader("Cargar datos experimentales")
data = pd.DataFrame({
    "Edad (días)": [0.5, 1, 3, 7, 14],
    "Resistencia (MPa)": [0.0, 5.0, 12.0, 20.0, 28.0]
})
edited_data = st.data_editor(data, num_rows="dynamic")

# ========================
# Funciones auxiliares
# ========================
def generar_pdf(edited_df: pd.DataFrame, a: float, b: float, r2: float, titulo: str) -> bytes:
    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    ax.scatter(edited_df["Madurez"], edited_df["Resistencia (MPa)"], label="Datos experimentales")
    x_fit = np.linspace(float(edited_df["Madurez"].min()), float(edited_df["Madurez"].max()), 200)
    y_fit = a * np.log10(x_fit) + b
    ax.plot(x_fit, y_fit, label="Curva estimada")
    ax.set_xlabel("Madurez (°C·h)")
    ax.set_ylabel("Resistencia a compresión (MPa)")
    ax.legend(loc="best")
    img_buf = BytesIO()
    plt.tight_layout()
    plt.savefig(img_buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    img_buf.seek(0)

    pdf_buf = BytesIO()
    doc = SimpleDocTemplate(pdf_buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(titulo, styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Temperatura laboratorio: {temp_lab:.1f} °C", styles["Normal"]))
    story.append(Paragraph(f"Temperatura datum: {temp_datum:.1f} °C", styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("📌 Resultados de la regresión", styles["Heading2"]))
    res_tab = Table([
        ["Pendiente (a)", f"{a:.2f}"],
        ["Ordenada al origen (b)", f"{b:.2f}"],
        ["R²", f"{r2:.2f}"],
    ], hAlign="LEFT")
    res_tab.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    story.append(res_tab)
    story.append(Spacer(1, 12))

    df_round = edited_df.copy()[["Edad (días)", "Resistencia (MPa)", "Madurez", "Log10(Madurez)"]].round(2)
    tabla_datos = [df_round.columns.tolist()] + df_round.values.tolist()
    t = Table(tabla_datos, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    story.append(Image(img_buf, width=430, height=270))

    doc.build(story)
    pdf_buf.seek(0)
    return pdf_buf.getvalue()

# ========================
# Cálculos
# ========================
if not edited_data.empty:
    madurez_factor = (temp_lab - temp_datum) * 24
    if madurez_factor <= 0:
        st.error("⚠️ (T_lab - T_datum) debe ser > 0")
        st.stop()

    edited_data["Madurez"] = madurez_factor * edited_data["Edad (días)"]
    edited_data = edited_data[edited_data["Madurez"] > 0]
    edited_data["Log10(Madurez)"] = np.log10(edited_data["Madurez"])

    X, Y = edited_data["Log10(Madurez)"].values, edited_data["Resistencia (MPa)"].values
    a, b = np.polyfit(X, Y, 1)
    Y_pred = a * X + b
    r2 = float(1 - (np.sum((Y - Y_pred) ** 2) / np.sum((Y - np.mean(Y)) ** 2)))

    # Gráfico interactivo
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edited_data["Madurez"], y=Y, mode="markers", name="Datos"))
    x_fit = np.linspace(float(edited_data["Madurez"].min()), float(edited_data["Madurez"].max()), 200)
    fig.add_trace(go.Scatter(x=x_fit, y=a*np.log10(x_fit)+b, mode="lines", name="Curva estimada"))
    st.plotly_chart(fig, use_container_width=True)

    # --- Generar Excel ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        edited_data.to_excel(writer, index=False, sheet_name="Datos")
        pd.DataFrame({"Pendiente (a)":[a],"Ordenada (b)":[b],"R²":[r2]}).to_excel(writer, index=False, sheet_name="Resultados")
    excel_bytes = output.getvalue()

    # --- Generar PDF ---
    pdf_bytes = generar_pdf(edited_data.copy(), a, b, r2, custom_title)

    # Guardar en sesión
    st.session_state["archivos_generados"].append(("calibracion.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
    st.session_state["archivos_generados"].append(("informe.pdf", pdf_bytes, "application/pdf"))

    # Descargas individuales
    st.download_button("📥 Descargar Excel", data=excel_bytes, file_name="calibracion.xlsx")
    st.download_button("📄 Descargar PDF", data=pdf_bytes, file_name="informe.pdf")

# ========================
# Descarga de todos juntos
# ========================
if st.session_state["archivos_generados"]:
    st.subheader("📦 Archivos generados en esta sesión")
    for fname, content, mime in st.session_state["archivos_generados"]:
        st.write(f"➡️ {fname}")
        st.download_button(f"⬇️ Descargar {fname}", data=content, file_name=fname, mime=mime, key=fname)
