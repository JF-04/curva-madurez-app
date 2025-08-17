import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Calibración estimada hormigones - IoT Provoleta")

st.markdown("""
Esta aplicación permite ingresar resultados de ensayos de resistencia a compresión y calcular 
la relación con la madurez (método de Nurse-Saul).
""")

# Entradas de temperatura
temp_lab = st.number_input("Temperatura de laboratorio (°C)", value=20.0, step=0.1)
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

    # Graficar puntos y curva de estimación
    fig, ax = plt.subplots()
    ax.scatter(X, Y, color="blue", label="Datos experimentales")

    X_fit = np.linspace(min(X), max(X), 100)
    Y_fit = a * X_fit + b
    ax.plot(X_fit, Y_fit, color="red", label="Recta de estimación")

    ax.set_xlabel("log10(Madurez) [log10(h·°C)]")
    ax.set_ylabel("Resistencia a compresión (MPa)")
    ax.set_title("Curva de calibración madurez vs resistencia")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    st.write("### Datos procesados")
    st.dataframe(edited_df)

