# Mutation Rate Calculator (Pandas Part 2)

A small, modular project that reads an **aligned FASTA** file and computes per-sequence
mutation rates **relative to a chosen reference sequence**. Results are assembled into a
Pandas `DataFrame` and can be saved to CSV.

## What counts as a “mutation”?
We compare each sequence to the chosen reference **column-by-column** in the alignment:
- Positions where **either** sequence has a gap (`-`) are **excluded** from the denominator.
- Among the remaining columns, a **mismatch** (different characters) counts as 1 mutation.
- Mutation rate = `mismatches / comparable_sites`.

> This behaves sensibly for gapped alignments and avoids inflating rates due to indels.

## Quickstart
```bash
# (optional) create and activate a Conda env
conda create -y -n pandas-part2 python=3.11 pandas numpy
conda activate pandas-part2

# run on the included toy alignment
python main.py --fasta example_alignment.fasta --ref Seq1 --out results.csv
```

You’ll see a table like:
```
    id  length  compared_sites  mismatches  mutation_rate
0  Seq1      30              30           0          0.00
1  Seq2      30              29           3          0.10
2  Seq3      30              28           4          0.14
```
And the CSV written to `results.csv`.

## Repo Layout
```
mutation_rate_calculator/
├── LICENSE
├── README.md
├── example_alignment.fasta
├── main.py
└── mut_calc/
    ├── __init__.py
    ├── fasta.py
    └── metrics.py
```

## CLI
```
python main.py --fasta <path> --ref <sequence_id> [--out results.csv] [--verbose]
```
- `--fasta`: path to an **aligned** FASTA file
- `--ref`: ID (header without the leading `>`) of the reference sequence
- `--out`: optional CSV output path (default: print only)
- `--verbose`: emit extra progress to `stderr`

## Testing
A tiny bash harness is provided:
```
bash run_tests.sh
```

## Error handling
- Missing file → written to `stderr` with exit code 2.
- Reference not found → `stderr` + exit code 3.
- Unequal alignment lengths → `stderr` + exit code 4.

## License
MIT (see `LICENSE`).
