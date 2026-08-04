"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Generador de Informes Ejecutivos PDF (reportlab), con portada institucional
(logos FIM/UNAP), metodologia, graficos, tablas de KPIs y recomendaciones
de formalizacion.

Autoras: Maria Isabel Nayde Zevallos Ttito / Arlet Maricielo Espezua Cuentas
"""

from __future__ import annotations
import io
import os
import datetime as dt
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, Image, PageBreak, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

from engine.data_models import (DepositProperties, GeochemistryParams, TreatmentPlant,
                                 SimulationConfig, RegulatoryLimits)
from engine.report_charts import fig_water_balance_mpl, fig_ard_geochem_mpl, fig_kpis_dashboard_mpl

BRAND_GREEN_DARK = colors.HexColor("#1B4D3E")
BRAND_GREEN_LIME = colors.HexColor("#8BC53F")
LIGHT_ROW = colors.HexColor("#F1F7F0")

AUTHORS = ["Maria Isabel Nayde Zevallos Ttito", "Arlet Maricielo Espezua Cuentas"]
COURSE_INFO = {
    "curso": "Introduccion a la Ciencia de Datos",
    "facultad": "Facultad de Ingenieria de Minas (FIM)",
    "universidad": "Universidad Nacional del Altiplano (UNA) - Puno",
    "semestre": "VIII Semestre",
}

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGO_FIM = os.path.join(REPO_ROOT, "fim.png")
LOGO_UNAP = os.path.join(REPO_ROOT, "unap.png")


def _fig_to_image(fig, width_cm=17.0):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    img_width = width_cm * cm
    aspect = fig.get_size_inches()[1] / fig.get_size_inches()[0]
    img_height = img_width * aspect
    return Image(buf, width=img_width, height=img_height)


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#666666"))
    footer_text = (f"AQUA-DAR PUNO v2.0  |  {COURSE_INFO['universidad']}  |  "
                   f"Autoras: {', '.join(AUTHORS)}  |  Pag. {doc.page}")
    canvas.drawCentredString(A4[0] / 2.0, 1.2 * cm, footer_text)
    canvas.restoreState()


def build_pdf_report(output_path: str,
                      config: SimulationConfig,
                      deposit: DepositProperties,
                      geochem: GeochemistryParams,
                      plant: TreatmentPlant,
                      limits: RegulatoryLimits,
                      df_sim: pd.DataFrame,
                      df_kpi: pd.DataFrame,
                      aba: dict,
                      summary: dict,
                      recommendations: list[str]) -> str:

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleGreen", parent=styles["Title"], textColor=BRAND_GREEN_DARK, fontSize=22)
    h2 = ParagraphStyle("H2Green", parent=styles["Heading2"], textColor=BRAND_GREEN_DARK)
    body = ParagraphStyle("BodyJust", parent=styles["BodyText"], alignment=TA_JUSTIFY, fontSize=9.5, leading=13)
    center = ParagraphStyle("Center", parent=styles["Normal"], alignment=TA_CENTER)

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             topMargin=1.6 * cm, bottomMargin=1.8 * cm,
                             leftMargin=1.8 * cm, rightMargin=1.8 * cm)
    story = []

    # --- Portada con logos ---------------------------------------------
    if os.path.exists(LOGO_UNAP) and os.path.exists(LOGO_FIM):
        logo_table = Table([[Image(LOGO_UNAP, width=2.6 * cm, height=2.6 * cm),
                              Image(LOGO_FIM, width=2.6 * cm, height=2.6 * cm)]],
                            colWidths=[9 * cm, 9 * cm])
        logo_table.setStyle(TableStyle([("ALIGN", (0, 0), (0, 0), "LEFT"),
                                         ("ALIGN", (1, 0), (1, 0), "RIGHT")]))
        story.append(logo_table)
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph("AQUA-DAR PUNO v2.0", title_style))
    story.append(Paragraph("Sistema Predictivo de Balance Hidrico y Drenaje Acido de Roca (DAR)",
                            ParagraphStyle("Subtitle", parent=styles["Heading3"], textColor=BRAND_GREEN_LIME,
                                           alignment=TA_CENTER)))
    story.append(Spacer(1, 0.6 * cm))
    story.append(HRFlowable(width="100%", color=BRAND_GREEN_DARK, thickness=1.2))
    story.append(Spacer(1, 0.8 * cm))

    story.append(Paragraph(f"<b>Proyecto:</b> {config.project_name}", center))
    story.append(Paragraph(f"<b>Deposito evaluado:</b> {deposit.name}", center))
    story.append(Paragraph(f"<b>Periodo simulado:</b> {config.start_year} - "
                            f"{config.start_year + config.n_years - 1} "
                            f"({config.n_years} anos, resolucion mensual)", center))
    story.append(Spacer(1, 1.2 * cm))

    story.append(Paragraph(f"<b>Curso:</b> {COURSE_INFO['curso']}", center))
    story.append(Paragraph(f"<b>{COURSE_INFO['facultad']} - {COURSE_INFO['semestre']}</b>", center))
    story.append(Paragraph(f"<b>{COURSE_INFO['universidad']}</b>", center))
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph("<b>Autoras:</b>", center))
    for a in AUTHORS:
        story.append(Paragraph(a, center))
    story.append(Spacer(1, 1.0 * cm))
    story.append(Paragraph(f"Fecha de generacion del informe: {dt.date.today().strftime('%d/%m/%Y')}", center))
    story.append(PageBreak())

    # --- Metodologia -----------------------------------------------------
    story.append(Paragraph("1. Metodologia y Alcance", h2))
    story.append(Paragraph(
        "El presente informe fue generado por el gemelo digital AQUA-DAR PUNO, desarrollado con fines "
        "academicos para el curso de Introduccion a la Ciencia de Datos. El modelo integra tres modulos: "
        "(1) Balance Hidrico mensual tipo 'bucket', con evapotranspiracion potencial estimada por el metodo "
        "de Thornthwaite corregido astronomicamente para la latitud del altiplano de Puno; (2) un modulo "
        "geoquimico de Balance Acido-Base (ABA) y cinetica de oxidacion de pirita de primer orden, modulada "
        "por temperatura y humedad, que predice la evolucion del pH y la liberacion de metales pesados "
        "(Fe, Cu, Zn); y (3) un modulo de indicadores (KPIs) que evalua la capacidad de la planta de "
        "tratamiento y el cumplimiento frente a la normativa ambiental peruana vigente "
        "(LMP D.S. N 010-2010-MINAM y ECA Agua D.S. N 004-2017-MINAM, Categoria 3).", body))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "El clima mensual se calibro con el boletin climatico oficial de SENAMHI para Puno (precipitacion "
        "de enero, mes mas lluvioso). Para un instrumento de gestion ambiental oficial (EIA / IGAFOM) se "
        "recomienda reemplazar estos datos por registros de estacion meteorologica y resultados de "
        "laboratorio (ABA/NAG) especificos del sitio.", body))
    story.append(Spacer(1, 0.4 * cm))

    param_table_data = [
        ["Parametro", "Valor"],
        ["Area del deposito (m2)", f"{deposit.area_m2:,.0f}"],
        ["Tonelaje del material (t)", f"{deposit.tonnage_material_t:,.0f}"],
        ["Coeficiente de escorrentia", f"{deposit.runoff_coefficient:.2f}"],
        ["% Azufre total (asumido piritico)", f"{geochem.percent_sulfur:.2f}%"],
        ["% Carbonato (CaCO3 eq.)", f"{geochem.percent_carbonate:.2f}%"],
        ["Capacidad planta de tratamiento (m3/dia)", f"{plant.capacity_m3_dia:,.0f}"],
        ["Mineral procesado (t/dia)", f"{plant.ore_processed_t_dia:,.0f}"],
    ]
    t = Table(param_table_data, colWidths=[9 * cm, 6 * cm])
    t.setStyle(_excel_style())
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    # --- Balance Acido-Base ----------------------------------------------
    story.append(Paragraph("2. Balance Acido-Base (ABA) del Material", h2))
    aba_data = [
        ["Indicador", "Valor"],
        ["Potencial Acido - AP (kg CaCO3-eq/t)", f"{aba['AP_kg_CaCO3_t']:.1f}"],
        ["Capacidad de Neutralizacion - ANC (kg CaCO3-eq/t)", f"{aba['ANC_kg_CaCO3_t']:.1f}"],
        ["Potencial Neto (NAPP = AP - ANC)", f"{aba['NAPP_kg_CaCO3_t']:.1f}"],
        ["Relacion ANC/AP", f"{aba['ratio_ANC_AP']:.2f}"],
        ["Clasificacion geoquimica", aba["clasificacion"]],
    ]
    t2 = Table(aba_data, colWidths=[10 * cm, 5 * cm])
    t2.setStyle(_excel_style())
    story.append(t2)
    story.append(Spacer(1, 0.5 * cm))

    # --- Graficos ----------------------------------------------------------
    story.append(Paragraph("3. Resultados: Balance Hidrico", h2))
    story.append(_fig_to_image(fig_water_balance_mpl(df_sim)))
    story.append(PageBreak())

    story.append(Paragraph("4. Resultados: Prediccion de Drenaje Acido de Roca", h2))
    story.append(_fig_to_image(fig_ard_geochem_mpl(df_sim, limits)))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("5. Indicadores Clave (KPIs) y Cumplimiento Normativo", h2))
    story.append(_fig_to_image(fig_kpis_dashboard_mpl(df_kpi, limits)))
    story.append(PageBreak())

    # --- Tabla resumen cumplimiento -----------------------------------------
    story.append(Paragraph("6. Resumen de Cumplimiento (LMP D.S. 010-2010-MINAM)", h2))
    comp_rows = [["Metal", "Limite LMP (mg/L)", "Conc. Promedio (mg/L)",
                  "Conc. Maxima (mg/L)", "% Cumplimiento", "Meses Excedidos"]]
    for metal in ("Fe", "Cu", "Zn"):
        if metal in summary:
            s = summary[metal]
            comp_rows.append([metal, f"{s['limite_lmp_mgL']:.2f}", f"{s['concentracion_promedio_mgL']:.3f}",
                               f"{s['concentracion_max_mgL']:.3f}", f"{s['pct_cumplimiento']:.1f}%",
                               str(s["meses_excedidos"])])
    t3 = Table(comp_rows, colWidths=[2.3 * cm, 3 * cm, 3.4 * cm, 3.2 * cm, 3 * cm, 3.1 * cm])
    t3.setStyle(_excel_style())
    story.append(t3)
    story.append(Spacer(1, 0.5 * cm))

    gen = summary.get("_general", {})
    story.append(Paragraph(
        f"La capacidad de la planta de tratamiento resulto suficiente en el "
        f"{gen.get('pct_capacidad_suficiente', 0):.1f}% de los meses simulados. El consumo de agua fresca "
        f"estimado es de {gen.get('consumo_agua_fresca_m3_t', 0):.3f} m3 por tonelada procesada.", body))
    story.append(Spacer(1, 0.5 * cm))

    # --- Recomendaciones -----------------------------------------------------
    story.append(Paragraph("7. Recomendaciones para Formalizacion e IGAFOM", h2))
    for i, rec in enumerate(recommendations, start=1):
        story.append(Paragraph(f"{i}. {rec}", body))
        story.append(Spacer(1, 0.15 * cm))

    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(
        "Nota: Los valores normativos citados (LMP D.S. N 010-2010-MINAM y ECA Agua D.S. N "
        "004-2017-MINAM Categoria 3) se presentan como referencia. Se recomienda verificar la vigencia y el "
        "texto oficial de la norma en las fuentes del MINAM/MINEM antes de su uso en un instrumento de "
        "gestion ambiental formal.", ParagraphStyle("Note", parent=body, fontSize=8, textColor=colors.grey)))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return output_path


def _excel_style() -> TableStyle:
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_GREEN_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_ROW]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B7C9BD")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])
