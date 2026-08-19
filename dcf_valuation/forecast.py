"""
Builds a year-by-year unlevered free cash flow (UFCF) forecast:

    Revenue -> EBIT -> NOPAT -> + D&A - CapEx - ΔNWC -> UFCF
"""

from dataclasses import dataclass, asdict
from typing import List
import pandas as pd

from .models import CompanyInputs


@dataclass
class YearForecast:
    year: int
    revenue: float
    ebit: float
    nopat: float
    da: float
    capex: float
    delta_nwc: float
    fcf: float


def forecast_fcf(inputs: CompanyInputs) -> pd.DataFrame:
    rows: List[YearForecast] = []

    prev_revenue = inputs.base_revenue
    for i in range(inputs.n_years):
        revenue = prev_revenue * (1 + inputs.revenue_growth[i])
        revenue_change = revenue - prev_revenue

        ebit = revenue * inputs.ebit_margin[i]
        nopat = ebit * (1 - inputs.tax_rate)

        da = revenue * inputs.da_pct_revenue[i]
        capex = revenue * inputs.capex_pct_revenue[i]
        delta_nwc = revenue_change * inputs.nwc_pct_revenue_change[i]

        fcf = nopat + da - capex - delta_nwc

        rows.append(YearForecast(
            year=i + 1,
            revenue=revenue,
            ebit=ebit,
            nopat=nopat,
            da=da,
            capex=capex,
            delta_nwc=delta_nwc,
            fcf=fcf,
        ))
        prev_revenue = revenue

    df = pd.DataFrame([asdict(r) for r in rows]).set_index("year")
    return df
