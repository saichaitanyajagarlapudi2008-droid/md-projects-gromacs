"""Relabel axes of a rectangular-box .gro so the old y axis becomes z.
Cyclic permutation (x, y, z) -> (z, x, y): a proper rotation, so handedness is kept.
Usage: python3 rotate_y_to_z.py in.gro out.gro
"""
import sys

inp, out = sys.argv[1], sys.argv[2]
lines = open(inp).read().splitlines()
title, n = lines[0], int(lines[1])
atoms, box = lines[2:2 + n], lines[2 + n].split()
if len(box) != 3:
    sys.exit("Box is not rectangular; this script only handles 3 box values.")

new = []
for l in atoms:
    head = l[:20]
    x, y, z = float(l[20:28]), float(l[28:36]), float(l[36:44])
    s = f"{head}{z:8.3f}{x:8.3f}{y:8.3f}"
    if len(l.rstrip()) >= 68:  # velocities present
        vx, vy, vz = float(l[44:52]), float(l[52:60]), float(l[60:68])
        s += f"{vz:8.4f}{vx:8.4f}{vy:8.4f}"
    new.append(s)

bx, by, bz = map(float, box)
with open(out, "w") as f:
    f.write("\n".join([title + " (rotated: old y is now z)", str(n)] + new
                      + [f"{bz:10.5f}{bx:10.5f}{by:10.5f}"]) + "\n")
print(f"box was {bx:.3f} {by:.3f} {bz:.3f}; now {bz:.3f} {bx:.3f} {by:.3f}")
