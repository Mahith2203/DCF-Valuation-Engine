#!/usr/bin/env python3
"""
CLI runner for the DCF Valuation Engine.

Usage:
    python run_dcf.py                          # uses example_inputs.json
    python run_dcf.py --config my_inputs.json
    python run_dcf.py --config my_inputs.json --csv out/sensitivity.csv
"""

import argparse
import json
import sys

import pandas as pd

from dcf_valuation import (
    CompanyInputs,
    WACCInputs,
    compute_wacc,
    run_dcf,
    sensitivity_table,
)

pd.set_option("display.float_format", lambda x: f"{x:,.2f}")


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Run a DCF valuation from a JSON config.")
    parser.add_argument("--config", default="example_inputs.json", help="Path to JSON input file.")
    parser.add_argument("--csv", default=None, help="Optional path to write the sensitivity table as CSV.")
    args = parser.parse_args()

    cfg = load_config(args.config)

    company = CompanyInputs(**cfg["company"])
    wacc_inputs = WACCInputs(**cfg["wacc"])

    wacc_breakdown = compute_wacc(wacc_inputs)
    wacc = wacc_breakdown["wacc"]

    result = run_dcf(company, wacc=wacc)

    print("=" * 60)
    print("WACC BREAKDOWN")
    print("=" * 60)
    for k, v in wacc_breakdown.items():
        print(f"{k:28s}: {v:.4%}" if k != "wacc" else f"{k:28s}: {v:.4%}")

    print("\n" + "=" * 60)
    print("UNLEVERED FCF FORECAST")
    print("=" * 60)
    print(result.forecast.round(1).to_string())

    print("\n" + "=" * 60)
    print("VALUATION SUMMARY")
    print("=" * 60)
    print(f"{'WACC':28s}: {result.wacc:.4%}")
    print(f"{'Terminal growth (g)':28s}: {result.terminal_growth:.4%}")
    print(f"{'PV of forecast FCF':28s}: {result.pv_fcf:,.1f}")
    print(f"{'Terminal value (undisc.)':28s}: {result.terminal_value:,.1f}")
    print(f"{'PV of terminal value':28s}: {result.pv_terminal_value:,.1f}")
    print(f"{'Enterprise value':28s}: {result.enterprise_value:,.1f}")
    print(f"{'Equity value':28s}: {result.equity_value:,.1f}")
    print(f"{'Fair value per share':28s}: {result.fair_value_per_share:,.2f}")

    sens_cfg = cfg.get("sensitivity")
    if sens_cfg:
        print("\n" + "=" * 60)
        print("SENSITIVITY: FAIR VALUE PER SHARE (rows=WACC, cols=terminal g)")
        print("=" * 60)
        table = sensitivity_table(
            company,
            wacc_range=sens_cfg["wacc_range"],
            growth_range=sens_cfg["growth_range"],
        )
        print(table.to_string())

        if args.csv:
            table.to_csv(args.csv)
            print(f"\nSensitivity table written to: {args.csv}")


if __name__ == "__main__":
    sys.exit(main())
