#!/usr/bin/env python3

"""
Main CLI app for the Mutation Rate Calculator (3+ sequence version).
--------------------------------------------------------------------

This script:
- Uses argparse for command-line interface (CLI)
- Reads aligned FASTA files with read_fa() from mut_calc.read
- Parses multiple sequences (3 or more) with parse_fa() from mut_calc.num
- Computes mutation rates with compare_to_reference() from mut_calc.metrics
- Outputs a Pandas DataFrame and writes results to CSV automatically

Example:
    python main.py --fasta mafft.aln-fasta --ref CB307934.1 --out mafft_results.csv --verbose
"""

from __future__ import annotations
import argparse, sys
import pandas as pd
from typing import Dict

# ✅ Import helper functions from your internal package
from mut_calc.read import read_fa
from mut_calc.num import parse_fa
from mut_calc.metrics import compare_to_reference


# ============================================================
# Main application class
# ============================================================

class MutationRateApp:
    def __init__(self, fasta_path: str = "example_alignment.fasta", ref_id: str = "Seq1",
                 out_csv: str = "results.csv", verbose: bool = False) -> None:
        """
        Initialize the mutation rate calculator.
        """
        self.fasta_path = fasta_path
        self.ref_id = ref_id
        self.out_csv = out_csv
        self.verbose = verbose

    def log(self, msg: str) -> None:
        """Print a message to stderr if verbose mode is enabled."""
        if self.verbose:
            print(msg, file=sys.stderr)

    def run(self) -> int:
        """
        Main workflow:
        1. Read FASTA file using read_fa()
        2. Parse sequences using parse_fa()
        3. Compare each sequence to the reference
        4. Output results to terminal and CSV
        """
        try:
            self.log(f"[INFO] Reading FASTA file using read_fa(): {self.fasta_path}")
            formatted_fasta = read_fa(self.fasta_path)

            # parse_fa() should now return lists: headers and sequences
            headers, sequences = parse_fa(formatted_fasta)

        except FileNotFoundError:
            print(f"[ERROR] File not found: {self.fasta_path}", file=sys.stderr)
            return 2
        except ValueError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            return 4

        # ✅ Build dictionary {header: sequence_string} dynamically
        seqs = {headers[i]: ''.join(sequences[i]) for i in range(len(headers))}

        try:
            self.log(f"[INFO] Computing mutation rates vs reference '{self.ref_id}'")
            stats = compare_to_reference(seqs, self.ref_id)
        except KeyError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            return 3

        # ✅ Convert stats to a pandas DataFrame
        df = pd.DataFrame([
            {
                "id": sid,
                "length": length,
                "compared_sites": compared,
                "mismatches": mismatches,
                "mutation_rate": rate
            }
            for sid, (length, compared, mismatches, rate) in stats.items()
        ]).sort_values("id").reset_index(drop=True)

        # ✅ Print and save
        print(df.to_string(index=False))
        df.to_csv(self.out_csv, index=False)
        self.log(f"[INFO] Wrote CSV: {self.out_csv}")

        return 0


# ============================================================
# Command-line argument handling
# ============================================================

def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parses command-line arguments."""
    p = argparse.ArgumentParser(description="Compute per-sequence mutation rates vs a reference from an aligned FASTA file.")
    p.add_argument("--fasta", default="example_alignment.fasta", help="Path to aligned FASTA file (default: example_alignment.fasta)")
    p.add_argument("--ref", default="Seq1", help="Reference sequence ID (default: Seq1)")
    p.add_argument("--out", dest="out_csv", default="results.csv", help="Output CSV path (default: results.csv)")
    p.add_argument("--verbose", action="store_true", help="Enable verbose logging to stderr")
    return p.parse_args(argv)


# ============================================================
# Program entry point
# ============================================================

def main(argv: list[str] | None = None) -> int:
    """Entry point for the command-line application."""
    ns = parse_args(sys.argv[1:] if argv is None else argv)
    app = MutationRateApp(ns.fasta, ns.ref, ns.out_csv, ns.verbose)
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())


