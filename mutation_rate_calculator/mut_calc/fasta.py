from typing import Dict, List, Tuple

def read_fasta_alignment(path: str) -> Dict[str, str]:
    """
    Read an aligned FASTA into a dict: {id: sequence}.
    Assumes all sequences are aligned to the same length.

    :raises ValueError: if sequences are not the same aligned length
    """
    ids: List[str] = []
    seqs: List[str] = []
    cur_id: str | None = None
    cur_seq: list[str] = []

    with open(path, "r") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if cur_id is not None:
                    ids.append(cur_id)
                    seqs.append("".join(cur_seq))
                cur_id = line[1:].strip()
                cur_seq = []
            else:
                cur_seq.append(line.upper())

        # flush last
        if cur_id is not None:
            ids.append(cur_id)
            seqs.append("".join(cur_seq))

    if not ids:
        raise ValueError("No sequences found in FASTA")

    # ensure equal length
    lengths = {len(s) for s in seqs}
    if len(lengths) != 1:
        raise ValueError(f"Sequences are not equal length (lengths seen: {sorted(lengths)})")

    return dict(zip(ids, seqs))
