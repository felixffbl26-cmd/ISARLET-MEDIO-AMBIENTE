"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Motor de Balance Hidrico Mensual.

Metodo de Thornthwaite (1948) para ETP, con correccion astronomica de
duracion del dia segun la latitud de Puno, acoplado a un modelo de
balance hidrico tipo "bucket" para estimar infiltracion, percolacion y
generacion mensual de lixiviado desde un deposito minero.

Autoras: Maria Isabel Nayde Zevallos Ttito / Arlet Mariciela Espezua Cuentas
"""

from __future__ import annotations
import math
import calendar
import numpy as np
import pandas as pd

from engine.data_models import DepositProperties


def _day_length_hours(latitude_deg: float, day_of_year: int) -> float:
    lat_rad = math.radians(latitude_deg)
    declination = math.radians(23.45 * math.sin(math.radians(360.0 / 365.0 * (284 + day_of_year))))
    cos_omega = -math.tan(lat_rad) * math.tan(declination)
    cos_omega = max(-1.0, min(1.0, cos_omega))
    omega_s = math.acos(cos_omega)
    return (24.0 / math.pi) * omega_s


def thornthwaite_correction_factor(latitude_deg: float, year: int, month: int) -> float:
    mid_month_doy = sum(calendar.monthrange(year, m)[1] for m in range(1, month)) + 15
    n_hours = _day_length_hours(latitude_deg, mid_month_doy)
    days_in_month = calendar.monthrange(year, month)[1]
    return (n_hours / 12.0) * (days_in_month / 30.0)


def thornthwaite_etp_series(df_climate: pd.DataFrame, latitude_deg: float) -> pd.Series:
    etp_values = np.zeros(len(df_climate))

    for year, group in df_climate.groupby("year"):
        temps = group["temp_mean_c"].clip(lower=0.0)
        heat_index = float(((temps / 5.0) ** 1.514).sum())
        if heat_index <= 0:
            etp_values[group.index] = 0.0
            continue
        a_exp = (6.75e-7 * heat_index ** 3 - 7.71e-5 * heat_index ** 2
                 + 1.792e-2 * heat_index + 0.49239)
        for idx, row in group.iterrows():
            t_mean = max(0.0, row["temp_mean_c"])
            if t_mean <= 0:
                etp_std = 0.0
            else:
                etp_std = 16.0 * ((10.0 * t_mean / heat_index) ** a_exp)
            k_corr = thornthwaite_correction_factor(latitude_deg, int(row["year"]), int(row["month"]))
            etp_values[idx] = etp_std * k_corr

    return pd.Series(etp_values, index=df_climate.index, name="etp_mm")


def run_water_balance(df_climate: pd.DataFrame, deposit: DepositProperties,
                       latitude_deg: float) -> pd.DataFrame:
    deposit.validate()
    df = df_climate.copy().reset_index(drop=True)
    df["etp_mm"] = thornthwaite_etp_series(df, latitude_deg)

    storage = deposit.initial_storage_mm
    runoff_list, aet_list, storage_list, percolation_list = [], [], [], []

    for _, row in df.iterrows():
        precip = row["precip_mm"]
        etp = row["etp_mm"]

        runoff = precip * deposit.runoff_coefficient
        effective_precip = precip - runoff

        available = storage + effective_precip
        aet = min(etp, available)
        storage_after_et = available - aet

        if storage_after_et > deposit.field_capacity_mm:
            percolation = storage_after_et - deposit.field_capacity_mm
            storage_new = deposit.field_capacity_mm
        else:
            percolation = 0.0
            storage_new = max(0.0, storage_after_et)

        runoff_list.append(runoff)
        aet_list.append(aet)
        storage_list.append(storage_new)
        percolation_list.append(percolation)
        storage = storage_new

    df["runoff_mm"] = runoff_list
    df["aet_mm"] = aet_list
    df["storage_mm"] = storage_list
    df["percolation_mm"] = percolation_list

    days_in_month = df.apply(lambda r: calendar.monthrange(int(r["year"]), int(r["month"]))[1], axis=1)
    df["days_in_month"] = days_in_month

    df["leachate_m3_mes"] = df["percolation_mm"] / 1000.0 * deposit.area_m2
    df["leachate_m3_dia"] = df["leachate_m3_mes"] / df["days_in_month"]

    return df
