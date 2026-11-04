#!/usr/bin/env python3
"""
End-to-end distance (Ree) and radius of gyration (Rg) of PVC chains, frame by frame.

How it works
  1. Reads [ bonds ] from the chain's .itp, keeps carbon-carbon bonds, and takes the
     longest carbon path as the backbone (40 C for a PVC 20-mer). Its two ends are the
     end-to-end atoms.
  2. Makes every chain whole across periodic boundaries by walking along its bonds
     (MDAnalysis unwrap), so chains split by the box edge are measured correctly.
  3. Ree = |r(last backbone C) - r(first backbone C)|,  Rg = mass-weighted radius of gyration.

Assumes the chains are the first N_CHAINS molecules in the .gro, in the same atom order as the .itp.

Usage
  python chain_ree.py system.gro traj.xtc PVC20.itp 16 --stride 250
  python chain_ree.py final.gro "" PVC20.itp 16            (single structure, no trajectory)

Output: summary on screen + chain_ree.csv (time, mean/std Ree and Rg) + chain_ree_perchain.csv
Needs:  pip install MDAnalysis networkx
"""
import sys, argparse, numpy as np, networkx as nx, MDAnalysis as mda

ap = argparse.ArgumentParser()
ap.add_argument('gro'); ap.add_argument('xtc'); ap.add_argument('itp'); ap.add_argument('nchains', type=int)
ap.add_argument('--stride', type=int, default=1, help='use every Nth frame')
a = ap.parse_args()

# ---- 1. chain topology from the .itp
names, bonds, sec = {}, [], None
for line in open(a.itp):
    s = line.split(';')[0].strip()
    if s.startswith('['): sec = s.strip('[] ').lower(); continue
    f = s.split()
    if sec == 'atoms' and len(f) >= 5 and f[0].isdigit(): names[int(f[0]) - 1] = f[4]
    if sec == 'bonds' and len(f) >= 2: bonds.append((int(f[0]) - 1, int(f[1]) - 1))
NA = len(names)
is_C = lambda i: names[i].upper().startswith('C') and not names[i].upper().startswith('CL')
g = nx.Graph(bonds)
gc = g.subgraph([i for i in g if is_C(i)])
ends = [n for n in gc if gc.degree(n) == 1]
backbone = max((nx.shortest_path(gc, x, y) for x in ends for y in ends if x < y), key=len)
print(f"{a.itp}: {NA} atoms per chain, backbone = {len(backbone)} carbons "
      f"(ends: {names[backbone[0]]} ... {names[backbone[-1]]})")

# ---- 2. universe + bonds for all chains
u = mda.Universe(a.gro, a.xtc) if a.xtc else mda.Universe(a.gro)
u.add_TopologyAttr('bonds', [(c*NA + i, c*NA + j) for c in range(a.nchains) for i, j in bonds])
chains = [u.atoms[c*NA:(c+1)*NA] for c in range(a.nchains)]
poly = u.atoms[:a.nchains*NA]
first = np.array([c*NA + backbone[0] for c in range(a.nchains)])
last = np.array([c*NA + backbone[-1] for c in range(a.nchains)])

# ---- 3. loop over frames
rows, per = [], []
for ts in u.trajectory[::a.stride]:
    poly.unwrap(compound='fragments')                          # make chains whole
    R = (u.atoms[last].positions - u.atoms[first].positions) / 10.0   # nm
    ree = np.linalg.norm(R, axis=1)
    rg = np.array([ch.radius_of_gyration() for ch in chains]) / 10.0
    tt = ts.time if ts.time is not None else 0.0
    rows.append((tt, ree.mean(), ree.std(), rg.mean(), rg.std()))
    per.append([tt] + list(ree))
rows = np.array(rows)
np.savetxt('chain_ree.csv', rows, delimiter=',', header='time_ps,Ree_mean_nm,Ree_std_nm,Rg_mean_nm,Rg_std_nm', comments='')
np.savetxt('chain_ree_perchain.csv', np.array(per), delimiter=',',
           header='time_ps,' + ','.join(f'chain{c+1}_Ree_nm' for c in range(a.nchains)), comments='')

t, rm, rs, gm, gs = rows[-1]
print(f"frames analysed: {len(rows)}   box: {u.dimensions[0]/10:.2f} nm")
print(f"last frame (t = {t:.0f} ps): Ree = {rm:.2f} +/- {rs:.2f} nm   Rg = {gm:.2f} +/- {gs:.2f} nm   (+/- = spread between chains)")
print(f"largest Ree seen: {np.array(per)[:,1:].max():.2f} nm (a fully stretched PVC 20-mer is ~4.9 nm; anything above that means a PBC problem)")
