from typing import Dict, Tuple

def compare_to_reference(seqs: Dict[str, str], ref_id: str) -> Dict[str, Tuple[int, int, int, float]]:
    """
    For each sequence, compute (length, compared_sites, mismatches, mutation_rate)
    relative to the reference sequence.
    - Exclude positions where either the query OR reference has a gap '-'
    - mutation_rate = mismatches / compared_sites (0 if compared_sites == 0)
    """
    if ref_id not in seqs:
        raise KeyError(f"Reference id '{ref_id}' not in FASTA")

    ref = seqs[ref_id]
    results: Dict[str, Tuple[int, int, int, float]] = {}

    for sid, seq in seqs.items():
        length = len(seq)
        compared = 0
        mismatches = 0
        for a, b in zip(seq, ref):
            if a == "-" or b == "-":
                continue
            compared += 1
            if a != b:
                mismatches += 1
        rate = (mismatches / compared) if compared else 0.0
        results[sid] = (length, compared, mismatches, round(rate, 6))
    return results
