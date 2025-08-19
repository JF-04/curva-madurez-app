import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

def generar_pdf(fig_data, edited_data, a, b, r2, titulo):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Título
    elements.append(Paragraph(f"<b>{titulo}</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Resultados
    results_text = f"""
    <b>Pendiente (a):</b> {a:.2f}<br/>
    <b>Ordenada (b):</b> {b:.2f}<br/>
    <b>R²:</b> {r2:.2f}
    """
    elements.append(Paragraph(results_text, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Tabla de datos
    table_data = [edited_data.columns.tolist()] + edited_data.values.tolist()
    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))

    # === Reemplazo de Kaleido: Matplotlib ===
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.scatter(edited_data["Madurez"], edited_data["Resistencia (MPa)"], color="blue", label="Datos experimentales")
    x_fit = np.linspace(min(edited_data["Madurez"]), max(edited_data["Madurez"]), 100)
    y_fit = a * np.log10(x_fit) + b
    ax.plot(x_fit, y_fit, color="red", label="Curva estimada")
    ax.set_xlabel("Madurez (°C.h)")
    ax.set_ylabel("Resistencia (MPa)")
    ax.legend()
    img_buf = BytesIO()
    plt.savefig(img_buf, format="png", bbox_inches="tight")
    plt.close(fig)
    img_buf.seek(0)

    elements.append(Image(img_buf, width=400, height=250))

    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
