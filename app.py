import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

st.title("Calibración estimada hormigones - IoT Provoleta")

# Entradas del usuario
temp_lab = st.number_input("Temperatura de laboratorio (°C):", value=23.0)
temp_datum = st.number_input("Temperatura datum (°C):", value=-10.0)

# Tabla editable
data = {
    "Edad (días)": [0.5, 1, 2, 3, 7, 14, 28],
    "Resistencia (MPa)": [0.0, 1.5, 5.0, 10.0, 20.0, 28.0, 35.0]
}
df = pd.DataFrame(data)
df = st.data_editor(df, num_rows="dynamic")

# Calcular madurez y log10(madurez)
df["Madurez"] = (temp_lab - temp_datum) * 24 * df["Edad (días)"]
df = df[df["Madurez"] > 0]  # evitar log10 de 0 o negativo
df["log10(Madurez)"] = np.log10(df["Madurez"])

# Ajuste por mínimos cuadrados
X = df["log10(Madurez)"].values
Y = df["Resistencia (MPa)"].values

if len(X) > 1:
    A = np.vstack([X, np.ones(len(X))]).T
    a, b = np.linalg.lstsq(A, Y, rcond=None)[0]

    # Predicciones
    Y_pred = a * X + b
    df["Resistencia estimada (MPa)"] = Y_pred

    # Calcular R²
    ss_res = np.sum((Y - Y_pred)**2)
    ss_tot = np.sum((Y - np.mean(Y))**2)
    r2 = 1 - ss_res/ss_tot

    # Mostrar resultados
    st.markdown(f"### Resultados de la regresión")
    st.markdown(f"**Pendiente (a):** {a:.4f}")
    st.markdown(f"**Ordenada (b):** {b:.4f}")
    st.markdown(f"**Coeficiente de determinación (R²):** {r2:.4f}")

    # Gráfico interactivo
    fig = go.Figure()

    # Datos experimentales
    fig.add_trace(go.Scatter(
        x=df["Madurez"], y=Y,
        mode="markers", name="Datos experimentales"
    ))

    # Curva estimada (línea suave)
    X_fit = np.linspace(min(df["Madurez"]), max(df["Madurez"]), 100)
    Y_fit = a * np.log10(X_fit) + b
    fig.add_trace(go.Scatter(
        x=X_fit, y=Y_fit,
        mode="lines", name="Curva estimada"
    ))

    # Anotación con R²
    fig.add_annotation(
        x=max(df["Madurez"]), y=max(Y),
        text=f"R² = {r2:.4f}",
        showarrow=False,
        font=dict(size=12, color="blue"),
        align="right"
    )

    fig.update_layout(
        xaxis_title="Madurez (°C·h)",
        yaxis_title="Resistencia a compresión (MPa)",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Exportar resultados a Excel ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Datos", index=False)

        # Hoja con parámetros de regresión
        resumen = pd.DataFrame({
            "Parámetro": ["Pendiente (a)", "Ordenada (b)", "R²"],
            "Valor": [a, b, r2]
        })
        resumen.to_excel(writer, sheet_name="Regresion", index=False)

    st.download_button(
        label="📥 Descargar resultados en Excel",
        data=output.getvalue(),
        file_name="calibracion_hormigon.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )





