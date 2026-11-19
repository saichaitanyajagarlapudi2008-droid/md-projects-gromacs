# PVC/DEHP blend: replication of Zhou & Milner (2018)

All-atom MD of poly(vinyl chloride) plasticised with di(2-ethylhexyl) phthalate, reproducing the density, glass transition and plasticiser dynamics reported in Zhou & Milner, *Macromolecules* 2018, 51, 3865–3873.

**Full write-up with figures:** [`PVC_DEHP_results.pdf`](PVC_DEHP_results.pdf)

## System

- 16 PVC 20-mers + 34 DEHP = 4,196 atoms (39.9 wt% DEHP; paper: 96 PVC + 200 DEHP, 39.4 wt%)
- OPLS-AA force field; two charge sets compared (LigParGen CM1A-LBCC and OPLS-AA table charges), checked against RESP charges from ORCA (HF/6-31G*, fitted with Multiwfn)
- GROMACS 2026, 1 fs time step, h-bond LINCS, PME, 1.2 nm cut-off, dispersion correction for energy and pressure

## Protocols

- **Slow cool (Tg):** 600 → 300 K at 6 K/ns, Parrinello–Rahman barostat
- **Quench cycles:** 600 K NPT → 300 K NPT, repeated, C-rescale barostat; automated in Bash with checkpoint restarts

## Key results

| Property | Method | Result |
| --- | --- | --- |
| Density, 300 K | NPT average after cycling | 1180 ± 2 kg/m³ (paper ≈ 1200) |
| Tg from density | Hyperbolic fit (paper's Eq. 1) | 340 ± 37 K |
| Tg from mobility | Kink in MSD vs T | ≈ 348 K (DEHP), ≈ 351 K (PVC) |
| DEHP diffusion | Einstein relation in 20 K windows of the slow cool, fitted only where the MSD is linear | 0.75 × 10⁻⁵ (570 K) → 0.20 × 10⁻⁵ cm²/s (490 K); ≤ 0.061 × 10⁻⁵ at 450 K (upper bound) |
| DEHP activation energy | Arrhenius fit of D(T), 390–590 K | ≈ 39 kJ/mol (38–42 depending on fit range) |
| PVC end-to-end distance | Per chain, 600 → 300 K | ≈ 2.4 → 2.9 nm |
| Compressibility κT, 300 K | Volume fluctuations | ≈ 4.0–4.5 × 10⁻¹⁰ Pa⁻¹ |

## Diffusion checks

The Einstein relation (MSD = 6Dt) only holds once the MSD is linear in time, so each 20 K window of the slow cool was checked on a log–log plot (slope α = 1 for normal diffusion).

- **Above ~490 K:** α ≈ 1, so D is reliable.
- **410–470 K:** α ≈ 0.75–0.85 (mildly subdiffusive), so these D values are upper bounds.
- **Below ~370 K:** α drops to 0.2–0.7. DEHP is caged in the PVC matrix as the system approaches Tg, so no diffusion coefficient is reported there.

Between 390 and 590 K the data are consistent with Arrhenius behaviour. A VFT fit gave no improvement (T₀ unconstrained), so any curvature is smaller than the scatter of single 3.3 ns windows. Resolving it would need longer constant-temperature runs or replicas.

The 1–2% density offset from the paper is attributed mainly to finite-size effects: the 3.6 nm box is smaller than the longest chain end-to-end distance (4.6 nm), whereas the paper used a ~6.5 nm box.

## Status

Ongoing: full-size replication (96 PVC 20-mers + 200 DEHP), longer constant-temperature runs for diffusion below 450 K, a 25 wt% composition and a box-size test.
