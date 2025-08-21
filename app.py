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

    # Encabezado con título y logo fijo a la derecha
    header_table = Table(
        [[Paragraph(custom_title, styles["Title"]), Paragraph("IoT Provoleta", styles["Normal"])]],
        colWidths=[400, 120]
    )
    header_table.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Temperatura laboratorio: {temp_lab:.1f} °C", styles["Normal"]))
    story.append(Paragraph(f"Temperatura datum: {temp_datum:.1f} °C", styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("📌 Resultados de la regresión", styles["Heading2"]))
    res_tab = Table([
        ["Ordenada al origen (b)", f"<b>{b:.2f}</b>"],
        ["Pendiente (a)", f"<b>{a:.2f}</b>"],
        ["R²", f"{r2:.2f}"],
    ], hAlign="LEFT")
    res_tab.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
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

    doc.build(story)
    pdf_buf.seek(0)
    return pdf_buf.getvalue()
