import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title("Calibración estimada hormigones - IoT Provoleta")

st.markdown("""
Esta aplicación permite ingresar resultados de ensayos de resistencia a compresión y calcular 
la relación con la madurez (método de Nurse-Saul).
""")

# Entradas de temperatura
temp_lab = st.number_input("Temperatura de laboratorio (°C)", value=23.0, step=0.1)
temp_datum = st.number_input("Temperatura datum (°C)", value=-10.0, step=0.1)

st.write("### Ingresar datos de ensayo")
st.markdown("Complete la tabla con edad en días (pueden ser decimales) y resistencia a compresión (MPa).")

# Tabla editable
data = {
    "Edad (días)": [1.0, 2.0, 3.0],
    "Resistencia (MPa)": [10.0, 15.0, 20.0],
}
df = pd.DataFrame(data)

edited_df = st.data_editor(df, num_rows="dynamic")

if not edited_df.empty:
    # Calcular madurez
    edited_df["Madurez"] = (temp_lab - temp_datum) * 24 * edited_df["Edad (días)"]
    edited_df["log10(Madurez)"] = np.log10(edited_df["Madurez"])

    X = edited_df["log10(Madurez)"].values
    Y = edited_df["Resistencia (MPa)"].values

    # Ajuste lineal por mínimos cuadrados
    a, b = np.polyfit(X, Y, 1)

    st.markdown("### Resultados de la regresión")
    st.success(f"**Pendiente (a): {a:.4f}**")
    st.success(f"**Ordenada al origen (b): {b:.4f}**")

    # Curva estimada: generar valores de madurez y calcular resistencia
    M_fit = np.linspace(min(edited_df["Madurez"]), max(edited_df["Madurez"]), 200)
    Y_fit = a * np.log10(M_fit) + b

    # Gráfico dinámico con Plotly
    fig = go.Figure()

    # Datos experimentales
    fig.add_trace(go.Scatter(
        x=edited_df["Madurez"],
        y=edited_df["Resistencia (MPa)"],
        mode="markers",
        name="Datos experimentales",
        marker=dict(color="blue", size=8),
        hovertemplate="Madurez: %{x:.1f}<br>Resistencia: %{y:.2f} MPa"
    ))

    # Curva estimada
    fig.add_trace(go.Scatter(
        x=M_fit,
        y=Y_fit,
        mode="lines",
        name="Curva estimada",
        line=dict(color="red", width=2),
        hovertemplate="Madurez: %{x:.1f}<br>Resistencia estimada: %{y:.2f} MPa"
    ))

    fig.update_layout(
        xaxis_title="Madurez (h·°C)",
        yaxis_title="Resistencia a compresión (MPa)",
        title="Curva de calibración: Madurez vs Resistencia",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write("### Datos procesados")
    st.dataframe(edited_df)



