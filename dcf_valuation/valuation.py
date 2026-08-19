"""
Discounts the UFCF forecast, applies a Gordon Growth terminal value, and
bridges Enterprise Value -> Equity Value -> Fair Value per Share.
"""

from dataclasses import dataclass
import pandas as pd

from .models import CompanyInputs
from .forecast import forecast_fcf


@dataclass
class DCFResult:
    forecast: pd.DataFrame
    wacc: float
    terminal_growth: float
    pv_fcf: float
    terminal_value: float
    pv_terminal_value: float
    enterprise_value: float
    equity_value: float
    fair_value_per_share: float


def _discount_factor(wacc: float, year: int) -> float:
    return 1 / ((1 + wacc) ** year)


def gordon_growth_terminal_value(final_year_fcf: float, wacc: float, g: float) -> float:
    if wacc <= g:
        raise ValueError("WACC must exceed the terminal growth rate for Gordon Growth to converge.")
    return final_year_fcf * (1 + g) / (wacc - g)


def run_dcf(inputs: CompanyInputs, wacc: float, terminal_growth: float | None = None) -> DCFResult:
    g = inputs.terminal_growth if terminal_growth is None else terminal_growth

    df = forecast_fcf(inputs)
    df["discount_factor"] = [_discount_factor(wacc, yr) for yr in df.index]
    df["pv_fcf"] = df["fcf"] * df["discount_factor"]

    pv_fcf_sum = df["pv_fcf"].sum()

    tv = gordon_growth_terminal_value(df["fcf"].iloc[-1], wacc, g)
    pv_tv = tv * df["discount_factor"].iloc[-1]

    enterprise_value = pv_fcf_sum + pv_tv
    equity_value = enterprise_value - inputs.net_debt
    fair_value_per_share = equity_value / inputs.shares_outstanding

    return DCFResult(
        forecast=df,
        wacc=wacc,
        terminal_growth=g,
        pv_fcf=pv_fcf_sum,
        terminal_value=tv,
        pv_terminal_value=pv_tv,
        enterprise_value=enterprise_value,
        equity_value=equity_value,
        fair_value_per_share=fair_value_per_share,
    )
