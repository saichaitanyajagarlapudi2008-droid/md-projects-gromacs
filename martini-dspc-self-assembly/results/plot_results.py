import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read_xvg(path):
    legends, rows, xlabel = [], [], ""
    for line in Path(path).read_text().splitlines():
        if line.startswith("@"):
            if "legend \"" in line and line.split()[1].startswith("s"):
                legends.append(line.split("legend", 1)[1].strip().strip('"'))
            elif "xaxis" in line and "label" in line:
                xlabel = line.split("label", 1)[1].strip().strip('"')
            continue
        if line.startswith("#") or not line.strip():
            continue
        rows.append([float(v) for v in line.split()])
    cols = list(zip(*rows))
    return cols[0], cols[1:], legends, xlabel


out = Path("figures")
out.mkdir(exist_ok=True)

t, ys, leg, _ = read_xvg("box.xvg")
box = dict(zip(leg, ys))
t_ns = [v / 1000 for v in t]
apl = [x * y / 64 for x, y in zip(box["Box-X"], box["Box-Y"])]
plt.figure(figsize=(6, 3.5))
plt.plot(t_ns, apl, lw=0.8)
plt.xlabel("Time (ns)")
plt.ylabel("Area per lipid (nm$^2$)")
plt.title("DSPC, Martini 3, 310 K")
plt.tight_layout()
plt.savefig(out / "area_per_lipid.png", dpi=200)
n = len(apl) // 2
print(f"Area per lipid, mean over second half: {sum(apl[n:]) / len(apl[n:]):.3f} nm^2")

t, ys, leg, _ = read_xvg("temp.xvg")
plt.figure(figsize=(6, 3.5))
plt.plot([v / 1000 for v in t], ys[0], lw=0.5)
plt.xlabel("Time (ns)")
plt.ylabel("Temperature (K)")
plt.tight_layout()
plt.savefig(out / "temperature.png", dpi=200)
print(f"Mean temperature: {sum(ys[0]) / len(ys[0]):.2f} K")

panels = [("density_x_rest_90ns.xvg", "x"), ("density_y_rest_90ns.xvg", "y"),
          ("density_z_rest_90ns.xvg", "z"), ("density_z_md3.xvg", "z (after rotation, 1 µs)")]
fig, axes = plt.subplots(1, 4, figsize=(14, 3.5))
for ax, (name, label) in zip(axes, panels):
    x, ys, leg, _ = read_xvg(name)
    for i, y in enumerate(ys):
        ax.plot(x, y, label=leg[i] if i < len(leg) else f"group {i + 1}")
    ax.set_xlabel(f"{label} (nm)")
    ax.set_title(name, fontsize=8)
axes[0].set_ylabel("Density (kg m$^{-3}$)")
axes[0].legend(fontsize=7)
plt.tight_layout()
plt.savefig(out / "density_profiles.png", dpi=200)
print("Figures written to figures/")
