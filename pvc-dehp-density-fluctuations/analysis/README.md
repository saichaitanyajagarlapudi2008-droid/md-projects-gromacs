# Analysis scripts

Chain-conformation analysis for the PVC/DEHP simulations.

| Script | What it does | Input | Output |
| --- | --- | --- | --- |
| `chain_ree.py` | End-to-end distance (Ree) and radius of gyration (Rg) of every PVC chain, frame by frame. Finds the carbon backbone from the `.itp` bonds and unwraps chains across periodic boundaries before measuring. | `.gro`, `.xtc`, chain `.itp`, number of chains | `chain_ree.csv`, `chain_ree_perchain.csv` |
| `ree_vs_T.py` | Converts time to temperature for a linear cooling run and averages Ree and Rg in temperature bins. | `chain_ree.csv` | `ree_rg_vs_T.csv` |

## Example

```
python chain_ree.py system.gro cool.xtc PVC20.itp 16 --stride 250
python ree_vs_T.py chain_ree.csv --t0 600 --rate 6 --bin 10
```

Requirements: Python 3, MDAnalysis, NumPy, networkx, pandas.

Scripts were written with AI assistance, then tested and adapted for this system.
