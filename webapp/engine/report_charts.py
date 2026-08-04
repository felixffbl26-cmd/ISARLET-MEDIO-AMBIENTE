"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Graficos estaticos (Matplotlib) usados unicamente para el informe PDF
exportable. El dashboard interactivo de la app usa Plotly (ver kpi_engine.py);
este modulo se mantiene separado porque reportlab necesita imagenes
rasterizadas y Matplotlib no requiere backend grafico ni dependencias
adicionales (funciona igual en un servidor headless como Streamlit Cloud).

Autoras: Maria Isabel Nayde Zevallos Ttito / Arlet Maricielo Espezua Cuentas
"""

from __future__ import annotations
import pandas as pd
from matplotlib.figure import Figure

from engine.data_models import RegulatoryLimits

METAL_COLORS = {"Fe": "#B0472B", "Cu": "#0B7285", "Zn": "#5F3DC4"}
BRAND_GREEN_DARK = "#1B4D3E"
WATER_TEAL = "#00838F"


def fig_water_balance_mpl(df: pd.DataFrame) -> Figure:
    fig = Figure(figsize=(9, 5), dpi=100)
    ax1 = fig.add_subplot(211)
    ax1.bar(df["date"], df["precip_mm"], color="#4DABF7", label="Precipitacion (mm)", width=20)
    ax1.plot(df["date"], df["etp_mm"], color="#E8590C", linewidth=1.8, label="ETP Thornthwaite (mm)")
    ax1.set_ylabel("mm / mes")
    ax1.set_title("Balance Hidrico Mensual - Cuenca del Deposito (Puno)")
    ax1.legend(loc="upper right", fontsize=8)
    ax1.grid(alpha=0.25)

    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.plot(df["date"], df["storage_mm"], color=WATER_TEAL, label="Almacenamiento (mm)")
    ax2.fill_between(df["date"], 0, df["percolation_mm"], color="#748FFC", alpha=0.5,
                      label="Percolacion / Lixiviado (mm)")
    ax2.set_ylabel("mm / mes")
    ax2.legend(loc="upper right", fontsize=8)
    ax2.grid(alpha=0.25)
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


def fig_ard_geochem_mpl(df: pd.DataFrame, limits: RegulatoryLimits) -> Figure:
    fig = Figure(figsize=(9, 5), dpi=100)
    ax1 = fig.add_subplot(211)
    ax1.plot(df["date"], df["pH_lixiviado"], color="#862E9C", linewidth=2)
    ax1.axhspan(6.0, 9.0, color="#40C057", alpha=0.12, label="Rango pH LMP (6-9)")
    ax1.set_ylabel("pH del lixiviado")
    ax1.set_title("Evolucion Predictiva del pH y Metales en el Lixiviado (DAR)")
    ax1.legend(loc="upper right", fontsize=8)
    ax1.grid(alpha=0.25)

    ax2 = fig.add_subplot(212, sharex=ax1)
    for metal, color in METAL_COLORS.items():
        col = f"{metal}_mgL"
        if col in df.columns:
            ax2.plot(df["date"], df[col], color=color, label=f"{metal} (mg/L)")
    ax2.axhline(limits.lmp_fe_mgL, color=METAL_COLORS["Fe"], linestyle="--", linewidth=0.9, alpha=0.7)
    ax2.axhline(limits.lmp_cu_mgL, color=METAL_COLORS["Cu"], linestyle="--", linewidth=0.9, alpha=0.7)
    ax2.axhline(limits.lmp_zn_mgL, color=METAL_COLORS["Zn"], linestyle="--", linewidth=0.9, alpha=0.7)
    ax2.set_yscale("log")
    ax2.set_ylabel("Concentracion (mg/L, escala log)")
    ax2.legend(loc="upper right", fontsize=8, ncol=3)
    ax2.grid(alpha=0.25, which="both")
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


def fig_kpis_dashboard_mpl(df_kpi: pd.DataFrame, limits: RegulatoryLimits) -> Figure:
    fig = Figure(figsize=(9, 7), dpi=100)

    ax1 = fig.add_subplot(311)
    ax1.bar(df_kpi["date"], df_kpi["efluente_tratado_m3_dia"], color=WATER_TEAL,
            label="Tratado (m3/dia)", width=20)
    ax1.bar(df_kpi["date"], df_kpi["efluente_no_tratado_m3_dia"], bottom=df_kpi["efluente_tratado_m3_dia"],
            color="#E03131", label="No tratado (m3/dia)", width=20)
    ax1.set_ylabel("m3 / dia")
    ax1.set_title("KPI 1: Efluente Tratado vs. No Tratado")
    ax1.legend(loc="upper right", fontsize=8)
    ax1.grid(alpha=0.25)

    ax2 = fig.add_subplot(312, sharex=ax1)
    for metal, color in METAL_COLORS.items():
        col = f"{metal}_descarga_mgL"
        if col in df_kpi.columns:
            ax2.plot(df_kpi["date"], df_kpi[col], color=color, label=f"{metal} descarga (mg/L)")
    ax2.axhline(limits.lmp_fe_mgL, color=METAL_COLORS["Fe"], linestyle="--", linewidth=0.9, alpha=0.7)
    ax2.axhline(limits.lmp_cu_mgL, color=METAL_COLORS["Cu"], linestyle="--", linewidth=0.9, alpha=0.7)
    ax2.axhline(limits.lmp_zn_mgL, color=METAL_COLORS["Zn"], linestyle="--", linewidth=0.9, alpha=0.7)
    ax2.set_ylabel("mg/L (post-tratamiento)")
    ax2.set_yscale("log")
    ax2.set_title("KPI 2: Metales en Punto de Descarga vs. LMP D.S. 010-2010-MINAM")
    ax2.legend(loc="upper right", fontsize=8, ncol=3)
    ax2.grid(alpha=0.25, which="both")

    ax3 = fig.add_subplot(313)
    consumo = df_kpi["consumo_agua_fresca_m3_t"].iloc[0]
    reciclaje = df_kpi["tasa_reciclaje_pct"].iloc[0]
    ax3.bar(["Agua Fresca (m3/t)", "Agua Reciclada (%)"], [consumo, reciclaje],
            color=[BRAND_GREEN_DARK, "#8BC53F"])
    ax3.set_title(f"KPI 3: Consumo de Agua Fresca = {consumo:.2f} m3/t | Reciclaje = {reciclaje:.0f}%")
    ax3.grid(alpha=0.25, axis="y")

    fig.autofmt_xdate()
    fig.tight_layout()
    return fig
