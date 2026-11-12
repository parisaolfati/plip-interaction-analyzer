# PLIP Interaction Analyzer

A Python tool to recursively parse Protein-Ligand Interaction Profiler (PLIP) `.txt` reports across multiple docking projects, filter interactions against key target protein residues, and generate local and master Excel summary reports.

## Features

- Recursively scans `complexes` directories for PLIP text reports (`*report*.txt`).
- Extracts Hydrophobic, Hydrogen Bond, Salt Bridge, pi-Stacking, and pi-Cation interactions between Chain A (protein) and Chain B (peptide/ligand).
- Filters interactions based on a predefined active-site residue set.
- Exports per-project `Detailed_Interaction_Results.xlsx` files and a ranked `Master_Screening_Report.xlsx`.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run in the current directory:
```bash
python analyze_plip.py
```

Or specify a custom screening directory and output filename:
```bash
python analyze_plip.py /path/to/screening_folder -o Custom_Master_Report.xlsx
```
