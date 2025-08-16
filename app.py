import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Calibración estimada de hormigones-IoT Provoleta")

# Inputs
temp_lab = st.number_input("Temperatura de laboratorio (°C)", value=20.0)
temp_datum = st.number_input("Temperatura datum (°C)", value=0.0)

st.markdown("### Ingresar datos de ensayo")
st.write("Cargue pares de Edad (días) y Resistencia (MPa):")

# Tabla editable
df = st.data_editor(
    pd.DataFrame({"Edad (días)": [1, 3, 7], "Resistencia (MPa)": [10.0, 
20.0, 30.0]}),
    num_rows="dynamic"
)

# Calcular madurez
df["Madurez"] = (temp_lab - temp_datum) * 24 * df["Edad (días)"]
df["log10(Madurez)"] = np.log10(df["Madurez"])

# Mínimos cuadrados
X = df["log10(Madurez)"].values
Y = df["Resistencia (MPa)"].values
a, b = np.polyfit(X, Y, 1)

st.markdown("### Resultados de regresión")
st.write(f"**Pendiente (a):** {a:.4f}")
st.write(f"**Ordenada al origen (b):** {b:.4f}")
st.write(f"Ecuación: Resistencia = {a:.4f}·log10(Madurez) + {b:.4f}")

# Gráfico
fig, ax = plt.subplots()
ax.scatter(X, Y, label="Datos")
ax.plot(X, a*X + b, color="red", label="Regresión")
ax.set_xlabel("log10(Madurez)")
ax.set_ylabel("Resistencia (MPa)")
ax.legend()
st.pyplot(fig)

