
    import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

st.title("Calibración estimada hormigones - IoT Provoleta")

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

# Calcular madurez y regresión
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

    st.markdown(f"### 📌 Resultados")
    st.markdown(f"**Pendiente (a):** {a:.3f}") 
    st.markdown(f"**Ordenada al origen (b):** {b:.3f}") 
    st.markdown(f"**R²:** {r2:.3f}")

    # Gráfico dinámico
    fig = go.Figure()

    # Puntos experimentales
    fig.add_trace(go.Scatter(
        x=edited_data["Madurez"], y=edited_data["Resistencia (MPa)"],
        mode="markers", name="Datos experimentales",
        marker=dict(size=8, color="blue")
    ))

    # Curva estimada (línea)
    x_fit = np.linspace(min(edited_data["Madurez"]), max(edited_data["Madurez"]), 100)
    y_fit = a * np.log10(x_fit) + b
    fig.add_trace(go.Scatter(
        x=x_fit, y=y_fit, mode="lines", name="Curva estimada",
        line=dict(color="red")
    ))

    fig.update_layout(
        xaxis_title="Madurez",
        yaxis_title="Resistencia a compresión (MPa)",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Exportar resultados
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        edited_data.to_excel(writer, index=False, sheet_name="Datos")
        pd.DataFrame({"Pendiente (a)": [a], "Ordenada (b)": [b], "R²": [r2]}).to_excel(writer, index=False, sheet_name="Resultados")
    st.download_button(
        label="📥 Descargar resultados en Excel",
        data=output.getvalue(),
        file_name="calibracion_hormigon.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )



