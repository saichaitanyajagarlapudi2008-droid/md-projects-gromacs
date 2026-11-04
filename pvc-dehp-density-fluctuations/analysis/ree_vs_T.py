#!/usr/bin/env python3
"""
Bin the per-frame Ree and Rg from chain_ree.py by temperature during a linear cooling run.

Temperature at time t (ps):  T = T0 - rate * t / 1000      (rate in K/ns)
Defaults match the slow cool used here: 600 K -> 300 K at 6 K/ns.

Usage
  python ree_vs_T.py                         (reads chain_ree.csv, defaults above)
  python ree_vs_T.py chain_ree.csv --t0 600 --rate 6 --bin 10

Output: table on screen + ree_rg_vs_T.csv (mean Ree and Rg per temperature bin, hottest first)
Needs:  pip install pandas
"""
import argparse
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("csv", nargs="?", default="chain_ree.csv")
ap.add_argument("--t0", type=float, default=600.0, help="starting temperature (K)")
ap.add_argument("--rate", type=float, default=6.0, help="cooling rate (K/ns)")
ap.add_argument("--bin", type=float, default=10.0, help="temperature bin width (K)")
a = ap.parse_args()

df = pd.read_csv(a.csv)
df["T_K"] = a.t0 - a.rate * df["time_ps"] / 1000.0
df["T_bin"] = (df["T_K"] // a.bin) * a.bin + a.bin / 2
out = (df.groupby("T_bin")[["Ree_mean_nm", "Rg_mean_nm"]]
         .mean()
         .sort_index(ascending=False))
print(out.round(3).to_string())
out.to_csv("ree_rg_vs_T.csv")
