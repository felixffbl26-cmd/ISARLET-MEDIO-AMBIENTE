"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Motor Geoquimico de Drenaje Acido de Roca (DAR).

Balance Acido-Base (ABA), cinetica de oxidacion de pirita de primer orden
modulada por temperatura y humedad, modelo de pH dinamico y liberacion
empirica de metales pesados (Fe, Cu, Zn).

Reaccion de referencia: FeS2 + 15/4 O2 + 7/2 H2O -> Fe(OH)3 + 2 H2SO4

Autoras: Maria Isabel Nayde Zevallos Ttito / Arlet Mariciela Espezua Cuentas
"""

from __future__ import annotations
import math
import numpy as np
import pandas as pd

from engine.data_models import DepositProperties, GeochemistryParams

FES2_MOLAR_MASS = 119.98
S_FRACTION_IN_FES2 = 64.13 / 119.98


def acid_base_accounting(deposit: DepositProperties, geochem: GeochemistryParams) -> dict:
    ap_kg_t = geochem.percent_sulfur * 31.25
    anc_kg_t = geochem.percent_carbonate * 10.0
    napp_kg_t = ap_kg_t - anc_kg_t
    ratio_anc_ap = (anc_kg_t / ap_kg_t) if ap_kg_t > 0 else float("inf")

    if ratio_anc_ap >= 3.0:
        classification = "No Generador de Acido (NAF)"
    elif ratio_anc_ap <= 1.0:
        classification = "Potencialmente Generador de Acido (PAF)"
    else:
        classification = "Incierto / Requiere Ensayo Cinetico (NAG)"

    ap_total_kg = deposit.tonnage_material_t * ap_kg_t
    anc_total_kg = deposit.tonnage_material_t * anc_kg_t

    return {
        "AP_kg_CaCO3_t": ap_kg_t,
        "ANC_kg_CaCO3_t": anc_kg_t,
        "NAPP_kg_CaCO3_t": napp_kg_t,
        "ratio_ANC_AP": ratio_anc_ap,
        "clasificacion": classification,
        "AP_total_kg": ap_total_kg,
        "ANC_total_kg": anc_total_kg,
    }


def _metal_concentration(ph: float, params: dict) -> float:
    base, cmax = params["base"], params["max"]
    ph_mid, steep = params["ph_mid"], params["steep"]
    return base + (cmax - base) / (1.0 + math.exp((ph - ph_mid) / steep))


def run_geochemistry_simulation(df_water_balance: pd.DataFrame,
                                 deposit: DepositProperties,
                                 geochem: GeochemistryParams):
    aba = acid_base_accounting(deposit, geochem)
    ap_total = aba["AP_total_kg"]
    anc_total = max(aba["ANC_total_kg"], 1e-6)

    pyrite_mass0_t = deposit.tonnage_material_t * (geochem.percent_sulfur / 100.0) / S_FRACTION_IN_FES2

    df = df_water_balance.copy().reset_index(drop=True)
    n = len(df)

    pyrite_mass = np.zeros(n)
    k_eff_arr = np.zeros(n)
    fraction_ox = np.zeros(n)
    cum_acid = np.zeros(n)
    ratio_acid_anc = np.zeros(n)
    ph_arr = np.zeros(n)
    metals = {m: np.zeros(n) for m in geochem.metal_params}

    m_prev = pyrite_mass0_t
    for i, row in df.iterrows():
        f_temp = geochem.q10_temperature ** ((row["temp_mean_c"] - geochem.reference_temp_c) / 10.0)
        f_moist = min(1.0, max(0.1, row["percolation_mm"] / max(deposit.percolation_reference_mm, 1e-6)))
        k_month = geochem.k_base_month * f_temp * f_moist

        m_new = m_prev * math.exp(-k_month)
        pyrite_mass[i] = m_new
        k_eff_arr[i] = k_month

        frac = 1.0 - (m_new / pyrite_mass0_t) if pyrite_mass0_t > 0 else 0.0
        fraction_ox[i] = frac

        acid_generated = ap_total * frac
        cum_acid[i] = acid_generated

        ratio = acid_generated / anc_total
        ratio_acid_anc[i] = ratio

        ph = geochem.ph_min + (geochem.ph_neutral - geochem.ph_min) / (1.0 + math.exp(6.0 * (ratio - 1.0)))
        ph_arr[i] = ph

        for metal, params in geochem.metal_params.items():
            metals[metal][i] = _metal_concentration(ph, params)

        m_prev = m_new

    df["pyrite_remaining_t"] = pyrite_mass
    df["k_eff_mensual"] = k_eff_arr
    df["fraccion_pirita_oxidada"] = fraction_ox
    df["acido_generado_kgCaCO3eq"] = cum_acid
    df["ratio_acido_ANC"] = ratio_acid_anc
    df["pH_lixiviado"] = ph_arr
    for metal in geochem.metal_params:
        df[f"{metal}_mgL"] = metals[metal]

    return df, aba
