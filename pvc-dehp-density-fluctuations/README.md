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
| DEHP diffusion | Einstein relation, 594 → 444 K | 0.87 → 0.063 × 10⁻⁵ cm²/s |
| DEHP activation energy | Arrhenius fit of D(T) | ≈ 39 kJ/mol |
| PVC end-to-end distance | Per chain, 600 → 300 K | ≈ 2.4 → 2.9 nm |
| Compressibility κT, 300 K | Volume fluctuations | ≈ 4.0–4.5 × 10⁻¹⁰ Pa⁻¹ |

The 1–2% density offset from the paper is attributed mainly to finite-size effects: the 3.6 nm box is smaller than the longest chain end-to-end distance (4.6 nm), whereas the paper used a ~6.5 nm box.

## Status

Ongoing: further temperature cycles, a 25 wt% composition and a box-size test.
