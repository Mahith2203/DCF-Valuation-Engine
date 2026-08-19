"""
Input schemas for the DCF engine.

All percentage fields are decimals (0.08 == 8%), all monetary fields are in the
same currency/units (e.g. millions) as `base_revenue`.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class CompanyInputs:
    # Starting point
    base_revenue: float                # Most recent full-year revenue
    net_debt: float                    # Total debt - cash & equivalents
    shares_outstanding: float

    # Forecast drivers (one value per forecast year, or a single value to hold flat)
    revenue_growth: List[float]        # e.g. [0.12, 0.10, 0.08, 0.06, 0.05]
    ebit_margin: List[float]           # e.g. [0.18, 0.19, 0.20, 0.20, 0.21]
    tax_rate: float                    # effective/marginal tax rate, flat across forecast
    da_pct_revenue: List[float]        # D&A as % of revenue
    capex_pct_revenue: List[float]     # CapEx as % of revenue
    nwc_pct_revenue_change: List[float]  # ΔNWC as % of the *change* in revenue

    # Terminal value
    terminal_growth: float = 0.025

    def __post_init__(self):
        n = len(self.revenue_growth)
        for name in ("ebit_margin", "da_pct_revenue", "capex_pct_revenue",
                     "nwc_pct_revenue_change"):
            vals = getattr(self, name)
            if len(vals) == 1:
                setattr(self, name, vals * n)
            elif len(vals) != n:
                raise ValueError(
                    f"'{name}' has {len(vals)} entries but revenue_growth has {n}; "
                    "lengths must match (or supply a single value to hold flat)."
                )

    @property
    def n_years(self) -> int:
        return len(self.revenue_growth)


@dataclass
class WACCInputs:
    risk_free_rate: float       # e.g. 0.042 (10Y treasury yield)
    equity_risk_premium: float  # e.g. 0.05
    beta: float                 # levered equity beta
    cost_of_debt: float         # pre-tax cost of debt
    tax_rate: float             # for the debt tax shield
    market_value_equity: float  # market cap
    market_value_debt: float    # total interest-bearing debt

    @property
    def cost_of_equity(self) -> float:
        return self.risk_free_rate + self.beta * self.equity_risk_premium

    @property
    def weights(self) -> "tuple[float, float]":
        total = self.market_value_equity + self.market_value_debt
        if total <= 0:
            raise ValueError("market_value_equity + market_value_debt must be > 0")
        return self.market_value_equity / total, self.market_value_debt / total
