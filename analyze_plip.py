# -*- coding: utf-8 -*-
import argparse
from pathlib import Path
import pandas as pd

# Default target protein residue set
DEFAULT_TARGET_RESIDUES = {
    "ASP358", "ALA356", "HIS383", "HIS387", "TYR523", 
    "HIS353", "ALA354", "HIS513", "GLN281", "LYS511", 
    "TYR520", "ARG522", "TRP357", "TYR146", "PHE512", 
    "TRP279", "TRP185", "GLN160", "GLU162"
}


def parse_plip_report(file_path: Path, target_residues: set) -> list:
    """Parse PLIP text report file and extract target protein-ligand interactions."""
    interactions = []
    current_type = None
    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # Identify interaction type
                if "**" in line:
                    if "Hydrophobic" in line:
                        current_type = "Hydrophobic"
                    elif "Hydrogen Bonds" in line:
                        current_type = "H-Bond"
                    elif "Salt Bridges" in line:
                        current_type = "Salt Bridge"
                    elif "pi-Stacking" in line:
                        current_type = "pi-Stacking"
                    elif "pi-Cation" in line:
                        current_type = "pi-Cation"
                    continue

                # Parse table rows
                if "|" in line and "RESNR" not in line and "====" not in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) > 6:
                        # Protein site (Chain A)
                        res_nr, res_type, res_chain = parts[1], parts[2], parts[3]
                        
                        # Ligand/Peptide site (Chain B)
                        lig_nr, lig_type = parts[4], parts[5]
                        
                        if res_chain == "A":
                            resid_protein = f"{res_type}{res_nr}".upper()
                            resid_ligand = f"{lig_type}{lig_nr}".upper()
                            
                            # Filter target residues
                            if resid_protein in target_residues:
                                dist = parts[8] if current_type == "H-Bond" else parts[6]
                                interactions.append({
                                    "Target_Protein": resid_protein,
                                    "Peptide_Residue": resid_ligand,
                                    "Interaction_Type": current_type,
                                    "Distance_A": dist
                                })
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return interactions


def analyze_interactions(root_dir: Path, output_name: str, target_residues: set):
    """Traverse 'complexes' subdirectories, parse PLIP reports, and export Excel summaries."""
    root_dir = root_dir.resolve()
    master_output = root_dir / output_name
    print(f"Starting interaction analysis in: {root_dir}")
    
    global_data = []

    for dirpath in root_dir.rglob("*"):
        if dirpath.is_dir() and dirpath.name.lower() == "complexes":
            project_name = dirpath.parent.name
            local_project_data = []
            
            # Search subdirectories for report files
            for report_file in dirpath.rglob("*.txt"):
                if "report" in report_file.name.lower():
                    model_label = report_file.name.split("_complex")[0].upper()
                    found = parse_plip_report(report_file, target_residues)
                    
                    for item in found:
                        local_project_data.append({"Model": model_label, **item})
                        global_data.append({
                            "Project": project_name,
                            "Model": model_label,
                            "Protein_Target": item["Target_Protein"],
                            "Peptide_Residue": item["Peptide_Residue"],
                            "Type": item["Interaction_Type"],
                            "Distance": item["Distance_A"]
                        })
            
            # Save local report for project
            if local_project_data:
                df_local = pd.DataFrame(local_project_data)
                local_out = dirpath / "Detailed_Interaction_Results.xlsx"
                with pd.ExcelWriter(local_out, engine="openpyxl") as writer:
                    df_local.to_excel(writer, sheet_name="Protein_Peptide_Pairs", index=False)
                    summary = df_local.groupby("Model").size().reset_index(name="Total_Hits")
                    summary.to_excel(writer, sheet_name="Summary", index=False)
                print(f" [Saved] Project report: {project_name}")

    # Save master report
    if global_data:
        df_global = pd.DataFrame(global_data)
        
        # Rank projects
        master_summary = df_global.groupby(["Project", "Model"]).size().reset_index(name="Hits_Count")
        master_summary = master_summary.sort_values(by="Hits_Count", ascending=False)
        
        with pd.ExcelWriter(master_output, engine="openpyxl") as writer:
            master_summary.to_excel(writer, sheet_name="Global_Ranking", index=False)
            df_global.to_excel(writer, sheet_name="All_Interactions_Detailed", index=False)
        
        print("\nProcessing completed successfully.")
        print(f"Master file saved to: {master_output}")
    else:
        print("\nNo matching interactions found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse PLIP text reports and summarize target residue interactions.")
    parser.add_argument(
        "root_dir",
        nargs="?",
        default=".",
        type=Path,
        help="Root directory containing project folders with 'complexes' subdirectories (default: current directory)."
    )
    parser.add_argument(
        "-o", "--output",
        default="Master_Screening_Report.xlsx",
        help="Filename for the master Excel summary report (default: Master_Screening_Report.xlsx)."
    )
    args = parser.parse_args()
    
    analyze_interactions(args.root_dir, args.output, DEFAULT_TARGET_RESIDUES)
