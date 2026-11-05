# Hydration free energy of ethanol in water

Alchemical decoupling of one ethanol molecule from water in GROMACS. This run follows the GROMACS free-energy tutorial for ethanol. I used it to learn how alchemical free-energy calculations are set up, run and analysed.

## Setup

| Item | Value |
| --- | --- |
| System | 1 ethanol in 2160 TIP3P waters |
| Force field | CHARMM36 with CGenFF parameters for ethanol (`lig1.itp`) |
| λ schedule | 31 windows: Coulomb switched off first (windows 0–10), then van der Waals (windows 11–30) |
| Soft-core | sc-alpha = 1.0, sc-power = 1, sc-sigma = 0.3 |
| Dynamics | stochastic dynamics (sd), 2 fs step, 298 K |
| Non-bonded | PME electrostatics, 1.2 nm; van der Waals cut-off 1.2 nm; no dispersion correction |
| Constraints | h-bonds (LINCS) |
| Output | dH/dλ and ΔH written every 10 steps |

### Workflow per window

| Stage | Settings | Length |
| --- | --- | --- |
| Energy minimisation | steepest descent | 5000 steps max |
| NVT | sd, 298 K, no barostat | 100 ps |
| NPT | sd, 298 K, Parrinello–Rahman (τp = 1 ps) | 100 ps |
| Production | sd, 298 K, Parrinello–Rahman (τp = 1 ps) | 1 ns |

## Changes from the tutorial

- **sc-alpha = 1.0 instead of the tutorial's 0.5.** In my earlier methane-in-water run, sc-alpha = 0.5 made the system blow up at λ = 0.25 and 0.8. A larger sc-alpha softens the core more strongly near the decoupled end, so I used 1.0 for every ethanol window.
- **pme_order = 4 instead of 6.** GROMACS only runs PME on the GPU with order 4. The system is small, so the accuracy loss is minor.

## What I learned

- **Why charges go first:** removing van der Waals while the charges are still on would let opposite charges on the solute and water collapse onto each other, so electrostatics are switched off before Lennard-Jones.
- **Why soft-core potentials are needed:** as Lennard-Jones interactions vanish, water can overlap the solute and the energy diverges (endpoint catastrophe). Soft-core potentials keep the energy finite near the end states.

## Files

- `input files/`: `em_*.mdp`, `nvt_*.mdp`, `npt_*.mdp`, `md_*.mdp` for windows 0–30, the topology (`topol.top`, `lig1.itp`) and starting structures (`lig1.gro`, `lig1_box.gro`, `solv.gro`)
- `Figures/`: free-energy differences between windows, the integrated free energy, and the final result in kJ/mol
- `Notes and terminal Screenshots.pdf`: notes and terminal output from the workflow
