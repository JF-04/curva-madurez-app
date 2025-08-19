 import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Exportar gráfico Plotly como imagen
import plotly.io as pio

# ========================
# CONFIGURACIÓN
# ========================

st.title("Calibración estimada hormigones - IoT Provoleta")

custom_title = st.text_input("📌 Ingrese un título para el informe:", "Informe de calibración")

st.markdown("""
Esta aplicación permite ingresar resultados de ensayos de resistencia a compresión y calcular 
la relación con la madurez (método de Nurse-Saul).
""")

# Entradas de temperatura
temp_lab = st.number_input("Temperatura de laboratorio (°C)", value=23.0, step=0.1)
temp_datum = st.number_input("Temperatura datum (°C)", value=-10.0, step=0.1)

# Tabla editable
st.subheader("Cargar datos experimentales")
data = pd.DataFrame({
    "Edad (días)": [0.5, 1, 3, 7, 14],
    "Resistencia (MPa)": [0.0, 5.0, 12.0, 20.0, 28.0]
})
edited_data = st.data_editor(data, num_rows="dynamic")

# ========================
# CÁLCULOS
# ========================
if not edited_data.empty:
    edited_data["Madurez"] = (temp_lab - temp_datum) * 24 * edited_data["Edad (días)"]
    edited_data["Log10(Madurez)"] = np.log10(edited_data["Madurez"])

    X = edited_data["Log10(Madurez)"].values
    Y = edited_data["Resistencia (MPa)"].values

    a, b = np.polyfit(X, Y, 1)  # pendiente y ordenada
    Y_pred = a * X + b

    # R²
    ss_res = np.sum((Y - Y_pred) ** 2)
    ss_tot = np.sum((Y - np.mean(Y)) ** 2)
    r2 = 1 - (ss_res / ss_tot)

    # ========================
    # GRÁFICO
    # ========================
    fig = go.Figure()

    # Puntos experimentales
    fig.add_trace(go.Scatter(
        x=edited_data["Madurez"], y=edited_data["Resistencia (MPa)"],
        mode="markers", name="Datos experimentales",
        marker=dict(size=8, color="blue")
    ))

    # Curva estimada
    x_fit = np.linspace(min(edited_data["Madurez"]), max(edited_data["Madurez"]), 100)
    y_fit = a * np.log10(x_fit) + b
    fig.add_trace(go.Scatter(
        x=x_fit, y=y_fit, mode="lines", name="Curva estimada",
        line=dict(color="red")
    ))

    fig.update_layout(
        xaxis_title="Madurez (°C.h)",
        yaxis_title="Resistencia a compresión (MPa)",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # ========================
    # EXPORTAR PDF CON TABLAS + GRÁFICO
    # ========================
    def generar_pdf(fig, edited_data):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Título
        story.append(Paragraph(custom_title, styles["Title"]))
        story.append(Spacer(1, 12))

        # Resultados de regresión
        story.append(Paragraph("📌 Resultados de la regresión:", styles["Heading2"]))
        data_tabla = [
            ["Pendiente (a)", f"{a:.2f}"],
            ["Ordenada al origen (b)", f"{b:.2f}"],
            ["R²", f"{r2:.2f}"]
        ]
        tabla = Table(data_tabla, hAlign="LEFT")
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ]))
        story.append(tabla)
        story.append(Spacer(1, 20))

        # Tabla de datos experimentales
        story.append(Paragraph("📊 Datos experimentales:", styles["Heading2"]))
        datos_exp = [list(edited_data.columns)] + edited_data.round(2).values.tolist()
        tabla_exp = Table(datos_exp, hAlign="CENTER")
        tabla_exp.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black)
        ]))
        story.append(tabla_exp)
        story.append(Spacer(1, 20))

        # Guardar gráfico Plotly como imagen
        img_buffer = BytesIO()
        pio.write_image(fig, img_buffer, format="png")
        img_buffer.seek(0)

        # Insertar imagen en el PDF
        story.append(Paragraph("📈 Gráfico Madurez vs Resistencia", styles["Heading2"]))
        story.append(Image(img_buffer, width=400, height=300))

        # Construir documento
        doc.build(story)
        pdf_value = buffer.getvalue()
        buffer.close()
        return pdf_value

    pdf_file = generar_pdf(fig, edited_data)
    st.download_button(
        label="📥 Descargar informe en PDF",
        data=pdf_file,
        file_name="informe_calibracion.pdf",
        mime="application/pdf"
    )
