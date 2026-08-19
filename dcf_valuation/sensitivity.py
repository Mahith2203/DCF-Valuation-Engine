"""
Builds a fair-value-per-share sensitivity table across a grid of
WACC and terminal growth (g) assumptions.
"""

from typing import Sequence
import pandas as pd

from .models import CompanyInputs
from .valuation import run_dcf


def sensitivity_table(
    inputs: CompanyInputs,
    wacc_range: Sequence[float],
    growth_range: Sequence[float],
) -> pd.DataFrame:
    """
    Returns a DataFrame indexed by WACC (rows) and terminal growth (columns),
    with fair value per share in each cell. len(wacc_range) x len(growth_range)
    scenarios are computed (5x5 = 25 by default).
    """
    data = {}
    for g in growth_range:
        col = []
        for w in wacc_range:
            try:
                result = run_dcf(inputs, wacc=w, terminal_growth=g)
                col.append(round(result.fair_value_per_share, 2))
            except ValueError:
                col.append(float("nan"))  # WACC <= g, undefined
        data[f"{g:.2%}"] = col

    table = pd.DataFrame(data, index=[f"{w:.2%}" for w in wacc_range])
    table.index.name = "WACC \\ g"
    return table
