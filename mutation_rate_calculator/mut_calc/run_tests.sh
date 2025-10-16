#!/usr/bin/env bash
set -euo pipefail

# If conda is installed, you can uncomment the next lines to create a fresh env:
# conda create -y -n pandas-part2 python=3.11 pandas numpy
# conda activate pandas-part2

echo "[TEST] Running mutation rate calculator on example_alignment.fasta"
python main.py --fasta example_alignment.fasta --ref Seq1 --out results.csv --verbose

echo "[TEST] Showing CSV:"
cat results.csv
