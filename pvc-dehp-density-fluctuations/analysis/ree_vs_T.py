import pandas as pd
df = pd.read_csv("chain_ree.csv")
print("columns:", list(df.columns))
t = df.iloc[:, 0]
df["T_K"] = 600 - 6 * t / 1000
ree = [c for c in df.columns if "ree" in c.lower()][0]
rg  = [c for c in df.columns if "rg" in c.lower()][0]
df["T_bin"] = (df["T_K"] // 10) * 10 + 5
out = df.groupby("T_bin")[[ree, rg]].mean().sort_index(ascending=False)
print(out.round(3).to_string())
out.to_csv("ree_rg_vs_T.csv")