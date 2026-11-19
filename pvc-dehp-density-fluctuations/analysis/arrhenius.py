import glob, re, numpy as np, matplotlib.pyplot as plt

R = 8.314
rows = []
for fn in glob.glob("msd_T*.xvg"):
    T = int(re.findall(r"T(\d+)", fn)[0])
    t, msd = np.loadtxt(fn, comments=("#", "@"), usecols=(0, 1), unpack=True)
    m = (t > 0) & (msd > 0)
    t, msd = t[m], msd[m]
    tmax = t[-1]
    sel = (t >= 0.10 * tmax) & (t <= 0.50 * tmax)
    alpha = np.polyfit(np.log10(t[sel]), np.log10(msd[sel]), 1)[0]
    slope = np.polyfit(t[sel], msd[sel], 1)[0]
    D = slope / 6 * 1e-2
    rows.append((T, alpha, D))

rows.sort(reverse=True)
print(f"{'T (K)':>6} {'alpha':>6} {'D (cm2/s)':>11}  status")
for T, a, D in rows:
    status = "valid" if a >= 0.9 else "subdiffusive (upper bound)"
    print(f"{T:>6} {a:>6.2f} {D:>11.3e}  {status}")

def arrhenius(subset, label):
    if len(subset) < 3:
        print(f"{label}: too few points"); return None
    T = np.array([r[0] for r in subset]); D = np.array([r[2] for r in subset])
    k, c = np.polyfit(1 / T, np.log(D), 1)
    print(f"{label}: Ea = {-k * R / 1000:.1f} kJ/mol  ({len(T)} windows, {T.min()}-{T.max()} K)")
    return k, c

valid = [r for r in rows if r[1] >= 0.9]
same_range = [r for r in rows if 440 <= r[0] <= 600]
fit_v = arrhenius(valid, "Valid windows only (alpha >= 0.9)")
fit_s = arrhenius(same_range, "All windows 440-600 K (like before)")

fig, ax = plt.subplots(figsize=(6, 4.5))
for T, a, D in rows:
    ax.plot(1000 / T, D, "o", color="C0" if a >= 0.9 else "C3")
if fit_v:
    x = np.linspace(1000 / 600, 1000 / 440, 50)
    ax.plot(x, np.exp(fit_v[1] + fit_v[0] * x / 1000), "C0-", label="fit: valid windows")
ax.set_yscale("log"); ax.set_xlabel("1000 / T (1/K)"); ax.set_ylabel("D (cm$^2$/s)")
ax.set_title("DEHP diffusion: blue = valid, red = subdiffusive")
ax.legend(); plt.tight_layout(); plt.savefig("arrhenius_checked.png", dpi=200)