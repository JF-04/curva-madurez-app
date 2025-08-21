import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- Para PDF con Matplotlib ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

st.title("Calibración estimada hormigones - IoT Provoleta")

# Título personalizado para informe/hoja
custom_title = st.text_input("📌 Título del informe/archivo", "Informe de calibración")

st.markdown("""
Esta aplicación permite ingresar resultados de ensayos de resistencia a compresión y calcular 
la relación con la madurez (método de Nurse-Saul).
""")

# Entradas
temp_lab = st.number_input("Temperatura de laboratorio (°C)", value=23.0, step=0.1)
temp_datum = st.number_input("Temperatura datum (°C)", value=-10.0, step=0.1)

st.markdown("""
Nota: Como temperatura datum (°C), usar por defecto -10°C. Caso contrario, determinar experimentalmente de acuerdo con la norma ASTM C1074.
""")

# Tabla editable
st.subheader("Cargar datos experimentales")
data = pd.DataFrame({
    "Edad (días)": [0.5, 1, 3, 7, 14],
    "Resistencia (MPa)": [0.0, 5.0, 12.0, 20.0, 28.0]
})
edited_data = st.data_editor(data, num_rows="dynamic")

def generar_pdf(edited_df: pd.DataFrame, a: float, b: float, r2: float) -> bytes:
    """Genera un PDF con resultados + tabla + gráfico renderizado."""
    # --- Gráfico Matplotlib ---
    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    ax.scatter(edited_df["Madurez"], edited_df["Resistencia (MPa)"], label="Datos experimentales", color="blue")
    x_fit = np.linspace(float(edited_df["Madurez"].min()), float(edited_df["Madurez"].max()), 200)
    y_fit = a * np.log10(x_fit) + b
    ax.plot(x_fit, y_fit, label="Curva estimada", color="red", linewidth=2)
    ax.set_xlabel("Madurez (°C·h)")
    ax.set_ylabel("Resistencia a compresión (MPa)")
    ax.legend(loc="best")
    img_buf = BytesIO()
    plt.tight_layout()
    plt.savefig(img_buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    img_buf.seek(0)

    # --- Construir PDF ---
    pdf_buf = BytesIO()
    doc = SimpleDocTemplate(pdf_buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Título del informe (desde la app)
    story.append(Paragraph(custom_title, styles["Title"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph(f"Temperatura laboratorio: {temp_lab:.1f} °C", styles["Normal"]))
    story.append(Paragraph(f"Temperatura datum: {temp_datum:.1f} °C", styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("📌 Resultados de la regresión", styles["Heading2"]))
    res_tab = Table([
        ["Ordenada al origen (b)", f"{b:.2f}"],
        ["Pendiente (a)", f"{a:.2f}"],
        ["R²", f"{r2:.2f}"],
    ], hAlign="LEFT")
    res_tab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 1), colors.lightgrey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    story.append(res_tab)
    story.append(Spacer(1, 12))

    story.append(Paragraph("📊 Datos experimentales", styles["Heading2"]))
    df_round = edited_df.copy()
    df_round = df_round[["Edad (días)", "Resistencia (MPa)", "Madurez", "Log10(Madurez)"]].round(2)
    tabla_datos = [df_round.columns.tolist()] + df_round.values.tolist()
    t = Table(tabla_datos, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    story.append(Paragraph("📈 Gráfico Madurez vs Resistencia", styles["Heading2"]))
    story.append(Image(img_buf, width=430, height=270))

    # Marca IoT Provoleta® abajo a la derecha
    story.append(Spacer(1, 30))
    story.append(Paragraph("<para align='right'>IoT Provoleta®</para>", styles["Normal"]))

    doc.build(story)
    pdf_buf.seek(0)
    return pdf_buf.getvalue()

# ========================
# CÁLCULOS
# ========================
if not edited_data.empty:
    # Madurez
    madurez_factor = (temp_lab - temp_datum) * 24
    if madurez_factor <= 0:
        st.error("⚠️ (T_lab - T_datum) debe ser > 0 para calcular la madurez.")
        st.stop()

    edited_data["Madurez"] = madurez_factor * edited_data["Edad (días)"]
    edited_data = edited_data[edited_data["Madurez"] > 0]
    edited_data["Log10(Madurez)"] = np.log10(edited_data["Madurez"])

    if len(edited_data) < 2:
        st.info("Cargá al menos dos puntos válidos para ajustar la regresión.")
        st.stop()

    X = edited_data["Log10(Madurez)"].values
    Y = edited_data["Resistencia (MPa)"].values

    a, b = np.polyfit(X, Y, 1)
    Y_pred = a * X + b

    ss_res = np.sum((Y - Y_pred) ** 2)
    ss_tot = np.sum((Y - np.mean(Y)) ** 2)
    r2 = float(1 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0

    st.markdown("### 📌 Resultados")
    st.markdown(f"<span style='color:green; font-weight:bold'>Pendiente (a): {a:.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:green; font-weight:bold'>Ordenada al origen (b): {b:.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"**R²:** {r2:.2f}")

    # --- Gráfico interactivo Plotly ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edited_data["Madurez"], y=edited_data["Resistencia (MPa)"],
        mode="markers", name="Datos experimentales",
        marker=dict(size=8, color="blue")
    ))
    x_fit_plot = np.linspace(float(edited_data["Madurez"].min()), float(edited_data["Madurez"].max()), 200)
    y_fit_plot = a * np.log10(x_fit_plot) + b
    fig.add_trace(go.Scatter(
        x=x_fit_plot, y=y_fit_plot, mode="lines", name="Curva estimada",
        line=dict(color="red")
    ))
    fig.update_layout(
        xaxis_title="Madurez (°C·h)",
        yaxis_title="Resistencia a compresión (MPa)",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- PDF ---
    pdf_bytes = generar_pdf(edited_data.copy(), a, b, r2)
    st.download_button(
        label="📄 Descargar informe en PDF",
        data=pdf_bytes,
        file_name="informe_calibracion.pdf",
        mime="application/pdf"
    )
