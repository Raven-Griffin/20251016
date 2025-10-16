#!/usr/bin/env python3
"""
Main CLI app for the Mutation Rate Calculator.
- Uses argparse for CLI
- Uses a class (`MutationRateApp`) to organize logic
- Emits human-readable output to stdout and progress/errors to stderr
- Assembles results in a Pandas DataFrame
"""
from __future__ import annotations
import argparse, sys
from typing import Dict
import pandas as pd
from mut_calc.fasta import read_fasta_alignment
from mut_calc.metrics import compare_to_reference

class MutationRateApp:
    def __init__(self, fasta_path: str, ref_id: str, out_csv: str | None = None, verbose: bool = False) -> None:
        self.fasta_path = fasta_path
        self.ref_id = ref_id
        self.out_csv = out_csv
        self.verbose = verbose

    def log(self, msg: str) -> None:
        if self.verbose:
            print(msg, file=sys.stderr)

    def run(self) -> int:
        try:
            self.log(f"[INFO] Reading FASTA: {self.fasta_path}")
            seqs: Dict[str, str] = read_fasta_alignment(self.fasta_path)
        except FileNotFoundError:
            print(f"[ERROR] File not found: {self.fasta_path}", file=sys.stderr)
            return 2
        except ValueError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            return 4

        try:
            self.log(f"[INFO] Computing mutation rates vs ref '{self.ref_id}'")
            stats = compare_to_reference(seqs, self.ref_id)
        except KeyError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            return 3

        # Build DataFrame
        rows = []
        for sid, (length, compared, mismatches, rate) in stats.items():
            rows.append({
                "id": sid,
                "length": length,
                "compared_sites": compared,
                "mismatches": mismatches,
                "mutation_rate": rate,
            })
        df = pd.DataFrame(rows).sort_values("id").reset_index(drop=True)

        # Pretty print to stdout
        print(df.to_string(index=False))

        # Optional CSV
        if self.out_csv:
            df.to_csv(self.out_csv, index=False)
            self.log(f"[INFO] Wrote CSV: {self.out_csv}")

        return 0

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compute per-sequence mutation rates vs a reference from an aligned FASTA.")
    p.add_argument("--fasta", required=True, help="Path to aligned FASTA file")
    p.add_argument("--ref", required=True, help="Reference sequence ID (header without '>')")
    p.add_argument("--out", dest="out_csv", default=None, help="Optional path to save CSV results")
    p.add_argument("--verbose", action="store_true", help="Verbose progress to stderr")
    return p.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    ns = parse_args(sys.argv[1:] if argv is None else argv)
    app = MutationRateApp(ns.fasta, ns.ref, ns.out_csv, ns.verbose)
    return app.run()

if __name__ == "__main__":
    raise SystemExit(main())
