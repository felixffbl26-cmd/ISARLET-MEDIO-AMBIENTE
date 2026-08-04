"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Modulo de Estructuras de Datos (Modelo)

Curso      : Introduccion a la Ciencia de Datos
Facultad   : Ingenieria de Minas (FIM) - VIII Semestre
Universidad: Universidad Nacional del Altiplano (UNA) - Puno
Autoras    : Maria Isabel Nayde Zevallos Ttito
             Arlet Mariciela Espezua Cuentas
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ClimateRecord:
    year: int
    month: int
    precip_mm: float
    temp_mean_c: float

    @property
    def period_label(self) -> str:
        return f"{self.year}-{self.month:02d}"


@dataclass
class DepositProperties:
    name: str = "Deposito de Desmonte de Mina"
    area_m2: float = 50_000.0
    tonnage_material_t: float = 500_000.0
    runoff_coefficient: float = 0.35
    field_capacity_mm: float = 40.0
    initial_storage_mm: float = 10.0
    percolation_reference_mm: float = 15.0

    def validate(self) -> None:
        if not (0.0 <= self.runoff_coefficient <= 1.0):
            raise ValueError("runoff_coefficient debe estar entre 0 y 1")
        if self.area_m2 <= 0 or self.tonnage_material_t <= 0:
            raise ValueError("area_m2 y tonnage_material_t deben ser positivos")


@dataclass
class GeochemistryParams:
    percent_sulfur: float = 3.5
    percent_carbonate: float = 0.5
    k_base_month: float = 0.018
    q10_temperature: float = 2.0
    reference_temp_c: float = 10.0
    ph_neutral: float = 7.8
    ph_min: float = 2.3

    metal_params: dict = field(default_factory=lambda: {
        "Fe": {"base": 0.50, "max": 380.0, "ph_mid": 4.4, "steep": 0.55},
        "Cu": {"base": 0.02, "max": 28.0, "ph_mid": 4.0, "steep": 0.45},
        "Zn": {"base": 0.05, "max": 130.0, "ph_mid": 4.7, "steep": 0.55},
    })


@dataclass
class TreatmentPlant:
    capacity_m3_dia: float = 180.0
    ore_processed_t_dia: float = 450.0
    fresh_water_intake_m3_dia: float = 320.0
    water_recycle_rate: float = 0.65
    removal_efficiency: dict = field(default_factory=lambda: {
        "Fe": 0.95, "Cu": 0.90, "Zn": 0.85,
    })


@dataclass
class SimulationConfig:
    project_name: str = "Proyecto Minero - Region Puno"
    start_year: int = 2024
    n_years: int = 5
    latitude_deg: float = -15.84
    altitude_msnm: float = 3825.0
    random_seed: Optional[int] = 42


@dataclass
class RegulatoryLimits:
    """
    Fuente: D.S. N 010-2010-MINAM, Anexo 1 (LMP efluentes minero-metalurgicos,
    valor en cualquier momento) y D.S. N 004-2017-MINAM (ECA Agua, Categoria 3:
    riego de vegetales y bebida de animales).
    """
    lmp_fe_mgL: float = 2.0
    lmp_cu_mgL: float = 0.5
    lmp_zn_mgL: float = 1.5
    lmp_ph_min: float = 6.0
    lmp_ph_max: float = 9.0
    lmp_sst_mgL: float = 50.0

    eca_cat3_fe_mgL: float = 5.0
    eca_cat3_cu_mgL: float = 0.2
    eca_cat3_zn_mgL: float = 2.0
