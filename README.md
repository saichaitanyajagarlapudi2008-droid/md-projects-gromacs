# md-projects-gromacs

Molecular dynamics projects run with GROMACS 2026 (built from source with GPU acceleration on Apple Silicon).

| Project | What it is | Status |
| --- | --- | --- |
| [`pvc-dehp-density-fluctuations`](pvc-dehp-density-fluctuations/) | All-atom MD of PVC plasticised with DEHP (39.9 wt%), replicating Zhou & Milner, *Macromolecules* 2018, 51, 3865–3873. Independent project. | Ongoing; results report and analysis code included |
| [`free-energy-ethanol-water`](free-energy-ethanol-water/) | Hydration free energy of ethanol by alchemical decoupling over 31 λ windows, following the GROMACS free-energy tutorial | Complete (learning exercise) |

Each folder has its own README.

## Tools

GROMACS 2026 · ORCA · Multiwfn · Python (MDAnalysis, NumPy, pandas) · Bash

Build notes for GROMACS on Apple Silicon (OpenCL, LibTorch, CP2K QM/MM): [BUILD_NOTES.md](BUILD_NOTES.md)
