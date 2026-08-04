"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Motor de KPIs, Cumplimiento Normativo y Graficos Interactivos (Plotly).

Calcula los indicadores clave solicitados:
  - Volumen de efluente tratado vs. no tratado (m3/dia)
  - Concentracion esperada de metales pesados en la descarga (mg/L Fe, Cu, Zn)
  - Consumo de agua fresca por tonelada procesada (m3/t)

Evalua el cumplimiento frente a la normativa ambiental peruana (LMP D.S.
010-2010-MINAM / ECA Agua D.S. 004-2017-MINAM) generando alertas utiles
como insumo para instrumentos de formalizacion minera (IGAFOM/REINFO).

Autoras: Maria Isabel Nayde Zevallos Ttito / Arlet Mariciela Espezua Cuentas
"""

from __future__ import annotations
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from engine.data_models import TreatmentPlant, RegulatoryLimits

METAL_COLORS = {"Fe": "#B0472B", "Cu": "#0B7285", "Zn": "#5F3DC4"}
BRAND_GREEN_DARK = "#1B4D3E"
BRAND_GREEN_LIME = "#8BC53F"
WATER_TEAL = "#00838F"


def compute_kpis(df_sim: pd.DataFrame, plant: TreatmentPlant) -> pd.DataFrame:
    df = df_sim.copy().reset_index(drop=True)

    df["efluente_generado_m3_dia"] = df["leachate_m3_dia"]
    df["efluente_tratado_m3_dia"] = np.minimum(df["efluente_generado_m3_dia"], plant.capacity_m3_dia)
    df["efluente_no_tratado_m3_dia"] = np.maximum(
        df["efluente_generado_m3_dia"] - plant.capacity_m3_dia, 0.0)

    total = df["efluente_generado_m3_dia"].replace(0, np.nan)
    for metal, eff in plant.removal_efficiency.items():
        raw_col = f"{metal}_mgL"
        if raw_col not in df.columns:
            continue
        treated_conc = df[raw_col] * (1.0 - eff)
        weighted = (df["efluente_tratado_m3_dia"] * treated_conc
                    + df["efluente_no_tratado_m3_dia"] * df[raw_col]) / total
        df[f"{metal}_descarga_mgL"] = weighted.fillna(df[raw_col])

    df["consumo_agua_fresca_m3_t"] = plant.fresh_water_intake_m3_dia / plant.ore_processed_t_dia
    df["tasa_reciclaje_pct"] = plant.water_recycle_rate * 100.0

    return df


def compliance_summary(df_kpi: pd.DataFrame, limits: RegulatoryLimits) -> dict:
    lmp = {"Fe": limits.lmp_fe_mgL, "Cu": limits.lmp_cu_mgL, "Zn": limits.lmp_zn_mgL}
    summary = {}
    for metal, limit in lmp.items():
        col = f"{metal}_descarga_mgL"
        if col not in df_kpi.columns:
            continue
        exceed = df_kpi[col] > limit
        summary[metal] = {
            "limite_lmp_mgL": limit,
            "meses_excedidos": int(exceed.sum()),
            "meses_totales": int(len(df_kpi)),
            "pct_cumplimiento": round(100.0 * (1 - exceed.mean()), 1),
            "concentracion_max_mgL": round(float(df_kpi[col].max()), 3),
            "concentracion_promedio_mgL": round(float(df_kpi[col].mean()), 3),
        }
    meses_no_tratados = int((df_kpi["efluente_no_tratado_m3_dia"] > 0.01).sum())
    summary["_general"] = {
        "meses_con_efluente_no_tratado": meses_no_tratados,
        "meses_totales": int(len(df_kpi)),
        "pct_capacidad_suficiente": round(100.0 * (1 - meses_no_tratados / max(len(df_kpi), 1)), 1),
        "consumo_agua_fresca_m3_t": round(float(df_kpi["consumo_agua_fresca_m3_t"].iloc[0]), 3),
    }
    return summary


def formalization_recommendations(aba: dict, summary: dict) -> list[str]:
    recs = []
    if "Generador" in aba["clasificacion"] and "No" not in aba["clasificacion"]:
        recs.append("El material presenta potencial NETO de generacion de acido (NAPP > 0). "
                     "Se recomienda incluir en el IGAFOM un sistema de cobertura/sellado y "
                     "encalado preventivo del deposito.")
    elif "Incierto" in aba["clasificacion"]:
        recs.append("La clasificacion ABA es incierta (relacion ANC/AP entre 1 y 3). Se recomienda "
                     "complementar con ensayos cineticos NAG/celdas de humedad antes de la "
                     "presentacion del instrumento de gestion ambiental.")
    else:
        recs.append("El material es predominantemente No Generador de Acido (NAF); mantener "
                     "monitoreo periodico de verificacion.")

    gen = summary.get("_general", {})
    if gen.get("meses_con_efluente_no_tratado", 0) > 0:
        recs.append(f"La planta de tratamiento resulta insuficiente en {gen['meses_con_efluente_no_tratado']} "
                     f"de {gen['meses_totales']} meses simulados. Se recomienda ampliar la capacidad de "
                     "tratamiento o implementar una poza de contingencia para picos de precipitacion "
                     "(Dic-Mar), requisito habitual en la evaluacion de instrumentos de formalizacion.")

    for metal in ("Fe", "Cu", "Zn"):
        if metal in summary and summary[metal]["pct_cumplimiento"] < 100.0:
            recs.append(f"Se proyectan excedencias del LMP para {metal} en "
                        f"{summary[metal]['meses_excedidos']} meses. Se recomienda evaluar un sistema de "
                        f"neutralizacion adicional (cal / caliza) antes del punto de descarga.")

    if gen.get("consumo_agua_fresca_m3_t", 0) > 1.0:
        recs.append("El consumo de agua fresca por tonelada procesada es elevado; se recomienda "
                     "incrementar la tasa de reciclaje de agua de planta para reducir la huella hidrica, "
                     "un criterio cada vez mas valorado en la evaluacion de instrumentos ambientales.")

    return recs


# --------------------------------------------------------------------------
# Graficos interactivos (Plotly) para el dashboard web
# --------------------------------------------------------------------------

def fig_water_balance(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.09,
                         subplot_titles=("Precipitacion vs. ETP (Thornthwaite)",
                                          "Almacenamiento y Percolacion / Lixiviado"))
    fig.add_trace(go.Bar(x=df["date"], y=df["precip_mm"], name="Precipitacion (mm)",
                          marker_color="#4DABF7"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["etp_mm"], name="ETP (mm)",
                              line=dict(color="#E8590C", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["storage_mm"], name="Almacenamiento (mm)",
                              line=dict(color=WATER_TEAL, width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["percolation_mm"], name="Percolacion / Lixiviado (mm)",
                              fill="tozeroy", line=dict(color="#748FFC")), row=2, col=1)
    fig.update_layout(height=560, hovermode="x unified", legend=dict(orientation="h", y=1.12),
                       margin=dict(t=60, l=10, r=10, b=10), plot_bgcolor="white", paper_bgcolor="white")
    fig.update_yaxes(title_text="mm / mes", row=1, col=1)
    fig.update_yaxes(title_text="mm / mes", row=2, col=1)
    return fig


def fig_ard_geochem(df: pd.DataFrame, limits: RegulatoryLimits) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.09,
                         subplot_titles=("Evolucion Predictiva del pH del Lixiviado",
                                          "Metales Pesados en el Lixiviado (mg/L, escala log)"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["pH_lixiviado"], name="pH",
                              line=dict(color="#862E9C", width=2.5)), row=1, col=1)
    fig.add_hrect(y0=6.0, y1=9.0, fillcolor="#40C057", opacity=0.10, line_width=0, row=1, col=1)

    for metal, color in METAL_COLORS.items():
        col = f"{metal}_mgL"
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df["date"], y=df[col], name=f"{metal} (mg/L)",
                                      line=dict(color=color, width=2)), row=2, col=1)
    for metal, limit in (("Fe", limits.lmp_fe_mgL), ("Cu", limits.lmp_cu_mgL), ("Zn", limits.lmp_zn_mgL)):
        fig.add_hline(y=limit, line_dash="dash", line_color=METAL_COLORS[metal], opacity=0.6, row=2, col=1)

    fig.update_yaxes(title_text="pH", row=1, col=1)
    fig.update_yaxes(title_text="mg/L", type="log", row=2, col=1)
    fig.update_layout(height=560, hovermode="x unified", legend=dict(orientation="h", y=1.12),
                       margin=dict(t=60, l=10, r=10, b=10), plot_bgcolor="white", paper_bgcolor="white")
    return fig


def fig_kpis_dashboard(df_kpi: pd.DataFrame, limits: RegulatoryLimits) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.11,
                         subplot_titles=("KPI 1: Efluente Tratado vs. No Tratado (m3/dia)",
                                          "KPI 2: Metales en Punto de Descarga vs. LMP (mg/L)"))
    fig.add_trace(go.Bar(x=df_kpi["date"], y=df_kpi["efluente_tratado_m3_dia"], name="Tratado",
                          marker_color=WATER_TEAL), row=1, col=1)
    fig.add_trace(go.Bar(x=df_kpi["date"], y=df_kpi["efluente_no_tratado_m3_dia"], name="No tratado",
                          marker_color="#E03131"), row=1, col=1)
    fig.update_layout(barmode="stack")

    for metal, color in METAL_COLORS.items():
        col = f"{metal}_descarga_mgL"
        if col in df_kpi.columns:
            fig.add_trace(go.Scatter(x=df_kpi["date"], y=df_kpi[col], name=f"{metal} descarga",
                                      line=dict(color=color, width=2)), row=2, col=1)
    for metal, limit in (("Fe", limits.lmp_fe_mgL), ("Cu", limits.lmp_cu_mgL), ("Zn", limits.lmp_zn_mgL)):
        fig.add_hline(y=limit, line_dash="dash", line_color=METAL_COLORS[metal], opacity=0.6, row=2, col=1)

    fig.update_yaxes(title_text="m3 / dia", row=1, col=1)
    fig.update_yaxes(title_text="mg/L (post-tratamiento)", type="log", row=2, col=1)
    fig.update_layout(height=620, hovermode="x unified", legend=dict(orientation="h", y=1.10),
                       margin=dict(t=60, l=10, r=10, b=10), plot_bgcolor="white", paper_bgcolor="white")
    return fig


def fig_water_consumption_gauge(consumo_m3_t: float, reciclaje_pct: float) -> go.Figure:
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "indicator"}, {"type": "indicator"}]])
    fig.add_trace(go.Indicator(
        mode="gauge+number", value=consumo_m3_t,
        title={"text": "Agua Fresca (m3/t)"},
        gauge={"axis": {"range": [0, 2.5]}, "bar": {"color": BRAND_GREEN_DARK},
               "steps": [{"range": [0, 0.8], "color": "#DCEFD8"},
                         {"range": [0.8, 1.5], "color": "#FFF3BF"},
                         {"range": [1.5, 2.5], "color": "#FFC9C9"}]},
    ), row=1, col=1)
    fig.add_trace(go.Indicator(
        mode="gauge+number", value=reciclaje_pct,
        title={"text": "Reciclaje de Agua (%)"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": BRAND_GREEN_LIME},
               "steps": [{"range": [0, 40], "color": "#FFC9C9"},
                         {"range": [40, 70], "color": "#FFF3BF"},
                         {"range": [70, 100], "color": "#DCEFD8"}]},
    ), row=1, col=2)
    fig.update_layout(height=260, margin=dict(t=40, l=20, r=20, b=10))
    return fig
