"""
CAPM-derived cost of equity and weighted average cost of capital (WACC).
"""

from .models import WACCInputs


def compute_wacc(w: WACCInputs) -> dict:
    """
    Returns a dict with cost_of_equity, after_tax_cost_of_debt, weights, and wacc.
    """
    cost_of_equity = w.cost_of_equity
    after_tax_cost_of_debt = w.cost_of_debt * (1 - w.tax_rate)
    weight_equity, weight_debt = w.weights

    wacc = weight_equity * cost_of_equity + weight_debt * after_tax_cost_of_debt

    return {
        "cost_of_equity": cost_of_equity,
        "after_tax_cost_of_debt": after_tax_cost_of_debt,
        "weight_equity": weight_equity,
        "weight_debt": weight_debt,
        "wacc": wacc,
    }
