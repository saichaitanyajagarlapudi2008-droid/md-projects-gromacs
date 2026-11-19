import sys, numpy as np, matplotlib.pyplot as plt
fn = sys.argv[1]
t, msd = np.loadtxt(fn, comments=("#", "@"), usecols=(0, 1), unpack=True)
m = (t > 0) & (msd > 0)
t, msd = t[m], msd[m]
lt, lm = np.log10(t), np.log10(msd)
alpha_local = np.gradient(lm, lt)

n = len(t)
print(fn)
for lo, hi in [(0, n // 10), (n // 10, n // 2), (n // 2, n)]:
    a, b = np.polyfit(lt[lo:hi], lm[lo:hi], 1)
    print(f"  t = {t[lo]:.0f}-{t[hi-1]:.0f} ps : slope alpha = {a:.2f}")

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].loglog(t, msd); ax[0].set_xlabel("t (ps)"); ax[0].set_ylabel("MSD (nm$^2$)")
ax[1].semilogx(t, alpha_local); ax[1].axhline(1, ls="--", c="k")
ax[1].set_xlabel("t (ps)"); ax[1].set_ylabel("local slope alpha")
fig.suptitle(fn)
plt.tight_layout(); plt.savefig(fn.replace(".xvg", "_loglog.png"), dpi=200)