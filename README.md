# DCF Valuation Engine

A lightweight, dependency-minimal Discounted Cash Flow (DCF) engine in Python.
Forecasts unlevered free cash flow, derives WACC via CAPM, applies a Gordon
Growth terminal value, and stress-tests fair value per share across a
WACC × terminal growth sensitivity grid.

## Features

- **Unlevered FCF forecast** — Revenue → EBIT → NOPAT → + D&A − CapEx − ΔNWC, driven by per-year growth, margin, and capex assumptions
- **CAPM-derived WACC** — cost of equity from risk-free rate, beta, and equity risk premium; blended with after-tax cost of debt
- **Gordon Growth terminal value** — discounted back and bridged from Enterprise Value → Equity Value → Fair Value per Share
- **Sensitivity grid** — fair value per share across a WACC × terminal growth matrix (5×5 = 25 scenarios by default, configurable)

## Project structure

```
dcf-valuation-engine/
├── dcf_valuation/
│   ├── __init__.py       # public API
│   ├── models.py         # CompanyInputs / WACCInputs dataclasses
│   ├── forecast.py        # revenue → unlevered FCF build-up
│   ├── wacc.py             # CAPM cost of equity + WACC
│   ├── valuation.py       # discounting, Gordon Growth TV, EV/Equity/share
│   └── sensitivity.py      # WACC x terminal growth grid
├── run_dcf.py              # CLI entry point
├── example_inputs.json     # sample company assumptions
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone https://github.com/<your-username>/dcf-valuation-engine.git
cd dcf-valuation-engine
pip install -r requirements.txt
```

Requires Python 3.10+ (uses `X | None` type hints).

## Quick start

Run the bundled example (5-year forecast for a hypothetical company):

```bash
python run_dcf.py
```

Run with your own assumptions:

```bash
python run_dcf.py --config my_inputs.json --csv out/sensitivity.csv
```

### Sample output

```
VALUATION SUMMARY
============================================================
WACC                        : 9.4050%
Terminal growth (g)         : 2.5000%
PV of forecast FCF          : 6,503.6
Terminal value (undisc.)    : 31,967.6
PV of terminal value        : 20,395.0
Enterprise value            : 26,898.7
Equity value                : 24,398.7
Fair value per share        : 48.80

SENSITIVITY: FAIR VALUE PER SHARE (rows=WACC, cols=terminal g)
============================================================
          1.50%  2.00%  2.50%  3.00%  3.50%
WACC \ g
8.00%     54.31  58.37  63.17  68.92  75.96
8.50%     49.88  53.29  57.28  61.99  67.64
9.00%     46.04  48.95  52.30  56.21  60.83
9.50%     42.69  45.18  48.03  51.33  55.17
10.00%    39.73  41.89  44.34  47.14  50.38
```

## Configuring your own model

Assumptions live in a JSON file (see `example_inputs.json`). Per-year driver
arrays (`revenue_growth`, `ebit_margin`, `da_pct_revenue`, `capex_pct_revenue`,
`nwc_pct_revenue_change`) can either have one entry per forecast year or a
single value that is held flat across the whole forecast.

```json
{
  "company": {
    "base_revenue": 10000,
    "net_debt": 2500,
    "shares_outstanding": 500,
    "revenue_growth": [0.12, 0.10, 0.09, 0.07, 0.05],
    "ebit_margin": [0.18, 0.19, 0.20, 0.20, 0.21],
    "tax_rate": 0.25,
    "da_pct_revenue": [0.04],
    "capex_pct_revenue": [0.05],
    "nwc_pct_revenue_change": [0.10],
    "terminal_growth": 0.025
  },
  "wacc": {
    "risk_free_rate": 0.042,
    "equity_risk_premium": 0.05,
    "beta": 1.15,
    "cost_of_debt": 0.06,
    "tax_rate": 0.25,
    "market_value_equity": 45000,
    "market_value_debt": 5000
  },
  "sensitivity": {
    "wacc_range": [0.08, 0.085, 0.09, 0.095, 0.10],
    "growth_range": [0.015, 0.02, 0.025, 0.03, 0.035]
  }
}
```

## Using it as a library

```python
from dcf_valuation import CompanyInputs, WACCInputs, compute_wacc, run_dcf, sensitivity_table

company = CompanyInputs(
    base_revenue=10_000,
    net_debt=2_500,
    shares_outstanding=500,
    revenue_growth=[0.12, 0.10, 0.09, 0.07, 0.05],
    ebit_margin=[0.20],
    tax_rate=0.25,
    da_pct_revenue=[0.04],
    capex_pct_revenue=[0.05],
    nwc_pct_revenue_change=[0.10],
    terminal_growth=0.025,
)

wacc_inputs = WACCInputs(
    risk_free_rate=0.042, equity_risk_premium=0.05, beta=1.15,
    cost_of_debt=0.06, tax_rate=0.25,
    market_value_equity=45_000, market_value_debt=5_000,
)

wacc = compute_wacc(wacc_inputs)["wacc"]
result = run_dcf(company, wacc=wacc)
print(result.fair_value_per_share)

table = sensitivity_table(company, wacc_range=[0.08, 0.09, 0.10], growth_range=[0.02, 0.025, 0.03])
print(table)
```

## Methodology notes

- **NOPAT** = EBIT × (1 − tax rate)
- **Unlevered FCF** = NOPAT + D&A − CapEx − ΔNWC
- **Cost of equity (CAPM)** = risk-free rate + β × equity risk premium
- **WACC** = (E / V) × cost of equity + (D / V) × cost of debt × (1 − tax rate)
- **Terminal value (Gordon Growth)** = FCF₍ₙ₎ × (1 + g) / (WACC − g), discounted at the final forecast year's factor
- **Equity value** = Enterprise value − net debt
- **Fair value per share** = Equity value / diluted shares outstanding

## Limitations

This is a standard build-and-discount DCF template, not investment advice. It
does not account for stock-based compensation dilution, multiple business
segments, mid-year discounting conventions, or probability-weighted scenarios.
Treat outputs as a starting point for sensitivity analysis, not a price target.

## License

MIT — see [LICENSE](LICENSE).
