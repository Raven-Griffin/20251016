#!/usr/bin/env python3
"""
num.py

Matrix and sequence utilities for the newu2 module.
This script defines the function parse_fa to transform
a formatted FASTA string into numpy arrays and an alignment matrix.
"""

import sys
import numpy as np
from typing import Tuple


#!/usr/bin/env python3
"""
num.py — Parsing utilities for Mutation Rate Calculator.
Handles aligned FASTA parsing for 2 or more sequences.
"""

import re
from typing import List, Tuple

def parse_fa(fasta_str: str) -> Tuple[List[str], List[List[str]]]:
    """
    Parse a formatted FASTA string into lists of headers and sequences.
    Supports any number of aligned sequences (2 or more).

    Parameters
    ----------
    fasta_str : str
        A formatted FASTA string returned by read_fa().

    Returns
    -------
    Tuple[List[str], List[List[str]]]
        headers   : list of sequence IDs (strings)
        sequences : list of sequences, each split into a list of characters

    Example
    -------
    Input FASTA:
        >Seq1
        ATGC
        >Seq2
        AT-T
        >Seq3
        ATGG

    Returns:
        headers   = ['Seq1', 'Seq2', 'Seq3']
        sequences = [['A','T','G','C'], ['A','T','-','T'], ['A','T','G','G']]
    """

    # Find all FASTA entries (header + sequence)
    entries = re.findall(r">(.*?)\n([^>]*)", fasta_str, flags=re.DOTALL)

    headers: List[str] = []
    sequences: List[List[str]] = []

    for header, seq in entries:
        # Take only the first token as ID (before any spaces)
        seq_id_match = re.match(r"^(\S+)", header.strip())
        seq_id = seq_id_match.group(1) if seq_id_match else "UNKNOWN"

        # Clean sequence (remove whitespace, uppercase)
        cleaned_seq = re.sub(r"\s+", "", seq).upper()

        headers.append(seq_id)
        sequences.append(list(cleaned_seq))

    if not headers or not sequences:
        raise ValueError("No valid FASTA entries found.")

    return headers, sequences

def fill_matrix(
    matrix: np.ndarray,
    seq1_array: np.ndarray,
    seq2_array: np.ndarray,
    match: int = 1,
    mismatch: int = -1,
    indel: int = -1
) -> np.ndarray:
    """
    Fill the scoring matrix using the Needleman–Wunsch down-pass algorithm.

    Parameters
    ----------
    matrix : np.ndarray
        A zero-initialized matrix of shape (len(seq2)+1, len(seq1)+1).
        Columns correspond to sequence 1; rows correspond to sequence 2.
    seq1_array : np.ndarray
        NumPy array of characters representing sequence 1.
    seq2_array : np.ndarray
        NumPy array of characters representing sequence 2.
    match : int, optional
        Score for a character match (default = +1).
    mismatch : int, optional
        Score for a character mismatch (default = -1).
    indel : int, optional
        Penalty for an insertion/deletion (default = -1).

    Returns
    -------
    np.ndarray
        The filled scoring matrix.

    Notes
    -----
    - The first cell (0,0) is initialized to 0.
    - The first row and column are filled using only indel penalties.
    - Each subsequent cell (i,j) is filled using:
        - diagonal = matrix[i-1, j-1] + (match or mismatch)
        - up       = matrix[i-1, j] + indel
        - left     = matrix[i, j-1] + indel
      The final cell value is max(diagonal, up, left).
    """
    
    rows, cols = matrix.shape
    
    # Initialize the first row and first column with indel penalties
    for i in range(1, rows):
        matrix[i, 0] = matrix[i - 1, 0] + indel
    sys.stdout.write(f"Initializing the first row with indel penalties:\n{matrix}\n")
    for j in range(1, cols):
        matrix[0, j] = matrix[0, j - 1] + indel
    sys.stdout.write(f"Initializing the first column with indel penalties:\n{matrix}\n")
        
    # Fill the matrix row by row
    sys.stdout.write("Filling up the matrix row by row:\n")
    for i in range(1, rows):
        for j in range(1, cols):
            # Compare corresponding characters
            if seq2_array[i - 1] == seq1_array[j - 1]:
                score_diagonal = matrix[i - 1, j - 1] + match
            else:
                score_diagonal = matrix[i - 1, j - 1] + mismatch
                
            # Indel scores
            score_up = matrix[i - 1, j] + indel
            score_left = matrix[i, j - 1] + indel
            
            # Take maximum
            max_value = max(score_diagonal, score_up, score_left)
            sys.stdout.write(f"Row {i}, column {j}: diagonal={score_diagonal}, up={score_up}, left={max_value} (max. = {max_value})\n")
            matrix[i, j] = max_value
            sys.stdout.write(f"{matrix}\n")
            
    return matrix

def trace_matrix(
    matrix: np.ndarray,
    seq1_array: np.ndarray,
    seq2_array: np.ndarray
) -> np.ndarray:
    """
    Trace back through the filled Needleman–Wunsch matrix to reconstruct
    the optimal alignment path.

    Parameters
    ----------
    matrix : np.ndarray
        The filled Needleman–Wunsch scoring matrix.
    seq1_array : np.ndarray
        NumPy array of characters representing sequence 1.
    seq2_array : np.ndarray
        NumPy array of characters representing sequence 2.

    Returns
    -------
    np.ndarray
        A NumPy array with two rows:
            - Row 0: aligned sequence 1
            - Row 1: aligned sequence 2
        Both aligned sequences have the same length.

    Notes
    -----
    - Tracing starts from the bottom-right corner.
    - At each step, we move in the direction that matches the cell's value:
        * Diagonal (match/mismatch)
        * Left  (gap in sequence 2)
        * Up    (gap in sequence 1)
    - When multiple paths are equally optimal:
        1. Prefer the diagonal move.
        2. If diagonal is not optimal, prefer the left move.
        3. Otherwise move up.
    """
    i, j = matrix.shape[0] - 1, matrix.shape[1] - 1
    aligned_seq1 = []
    aligned_seq2 = []
    
    while i > 0 or j > 0:
        # Handle boundaries first
        if i == 0:
            aligned_seq1.append(seq1_array[j - 1])
            aligned_seq2.append('-')
            j -= 1
            continue
        elif j == 0:
            aligned_seq1.append('-')
            aligned_seq2.append(seq2_array[i - 1])
            i -= 1
            continue
        
        current = matrix[i, j]
        diag = matrix[i - 1, j - 1]
        up = matrix[i - 1, j]
        left = matrix[i, j - 1]
        
        # Determine which move leads to current
        if current == diag + 1 or current == diag - 1:
            # Diagonal move (priority 1)
            aligned_seq1.append(seq1_array[j - 1])
            aligned_seq2.append(seq2_array[i - 1])
            i -= 1
            j -= 1
        elif current == left - 1:
            # Move left (gap in seq2, priority 2)
            aligned_seq1.append(seq1_array[j - 1])
            aligned_seq2.append('-')
            j -= 1
        else:
            # Move up (gap in seq1, priority 3)
            aligned_seq1.append('-')
            aligned_seq2.append(seq2_array[i - 1])
            i -= 1
            
    aligned_seq1.reverse()
    aligned_seq2.reverse()
    
    return np.array([aligned_seq1, aligned_seq2])