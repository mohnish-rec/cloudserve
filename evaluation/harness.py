"""The evaluation harness in the form the Build Specification shows (section 04, "A reasonable command structure"):

    python -m evaluation.harness --input data/validation_tickets.json --output evaluation/results/

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
It runs exactly the same unattended run as `python -m src.run_evaluation <input> <output file>` (A9, A10): every
ticket in the file, nobody intervening, every decision logged, the metrics report written at the end. --output may be
a folder (the results file is named after the input, e.g. validation_tickets_results.json) or a .json file name.
The reply cache stays off, as for every validation, hidden-set and final run (D-025).
"""
import argparse
from pathlib import Path


def output_file(input_path: str, output: str) -> Path:
    out = Path(output)
    if out.suffix.lower() == ".json":
        return out
    return out / f"{Path(input_path).stem}_results.json"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Run a whole ticket file through the system, unattended.")
    ap.add_argument("--input", required=True, help="the tickets file, e.g. data/validation_tickets.json")
    ap.add_argument("--output", required=True, help="a folder for the results, or a .json file name")
    ap.add_argument("--metrics-port", type=int, default=None, help="serve Prometheus metrics while running (e.g. 8001)")
    a = ap.parse_args(argv)
    from src.run_evaluation import run_evaluation
    return run_evaluation(a.input, str(output_file(a.input, a.output)), a.metrics_port)


if __name__ == "__main__":
    main()
