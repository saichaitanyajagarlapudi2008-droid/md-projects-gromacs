# Analysis scripts

Chain-conformation and DEHP-diffusion analysis for the PVC/DEHP simulations.

| Script | What it does | Input | Output |
| --- | --- | --- | --- |
| `chain_ree.py` | End-to-end distance (Ree) and radius of gyration (Rg) of every PVC chain, frame by frame. Finds the carbon backbone from the `.itp` bonds and unwraps chains across periodic boundaries before measuring. | `.gro`, `.xtc`, chain `.itp`, number of chains | `chain_ree.csv`, `chain_ree_perchain.csv` |
| `ree_vs_T.py` | Converts time to temperature for a linear cooling run and averages Ree and Rg in temperature bins. | `chain_ree.csv` | `ree_rg_vs_T.csv` |
| `run_windows.sh` | MSD of DEHP centres of mass (`gmx msd -mol`) in 20 K windows of the 600 → 300 K slow cool. | cooling `.xtc` and `.tpr` (arguments 1 and 2) | `msd_T*.xvg` |
| `loglog.py` | Log–log MSD slope (α) for one window, to check where the MSD is linear (α = 1). | one `msd_T*.xvg` | slopes on screen, `*_loglog.png` |
| `arrhenius.py` | D from the linear part of each window, flags subdiffusive windows (α < 0.9) as upper bounds, Arrhenius fit. | all `msd_T*.xvg` | table on screen, `arrhenius_checked.png` |

## Example

```
python chain_ree.py system.gro cool.xtc PVC20.itp 16 --stride 250
python ree_vs_T.py chain_ree.csv --t0 600 --rate 6 --bin 10
bash run_windows.sh new_annealing.xtc anneal_40.tpr
python loglog.py msd_T570.xvg
python arrhenius.py
```

Requirements: Python 3, MDAnalysis, NumPy, networkx, pandas, matplotlib; GROMACS for `run_windows.sh`.

Scripts were written with AI assistance, then tested and adapted for this system.
