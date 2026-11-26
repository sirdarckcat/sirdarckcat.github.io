import math, numpy as np
from vlib import *
cov, rows = get(); N0, M, K = win(cov)
s, s2 = 499, 1637
a = tab(rows, s).astype(float); b = tab(rows, s2).astype(float)
# in the window label k: x(k) = a[(N0 + kM) mod s] = sum_h A_h e(h (N0+kM)/s)
Pa = np.abs(np.fft.fft(a)) ** 2 / (s * a.var()); Pb = np.abs(np.fft.fft(b)) ** 2 / (s2 * b.var())
H, H2 = np.meshgrid(np.arange(1, s), np.arange(1, s2), indexing="ij")
num = ((H * s2 * (M % s) % (s * s2)) * 1 + (H2 * s * (M % s2)) % (s * s2))   # (h M/s + h' M/s') * s s'  mod s s'
# careful: h*M/s mod 1 = (h*(M mod s) mod s)/s ; write over common denominator
th = (((H * (M % s)) % s) * s2 + ((H2 * (M % s2)) % s2) * s) % (s * s2) / (s * s2)
dist = np.minimum(th, 1 - th)
w = np.sqrt(Pa[1:][:, None] * Pb[1:][None, :])
near = dist < 1.0 / (1 << 17)
print("resonant pairs (||theta|| < 2^-17):", int(near.sum()), "of", near.size)
idx = np.argsort(-(w * near).ravel())[:5]
for i in idx:
    h, h2 = np.unravel_index(i, w.shape); print("  h=%d (h/s=%.4f, P=%.1f, rank %d of %d)  h'=%d (h'/s'=%.4f, P=%.1f, rank %d of %d)  ||theta||*2^20 = %.3f" % (h + 1, (h + 1) / s, Pa[h + 1], (Pa[1:] > Pa[h + 1]).sum() + 1, s - 1, h2 + 1, (h2 + 1) / s2, Pb[h2 + 1], (Pb[1:] > Pb[h2 + 1]).sum() + 1, s2 - 1, dist[h, h2] * (1 << 20)))
print("largest P at 499: %.1f, at 1637: %.1f ; ln s: %.1f %.1f" % (Pa[1:].max(), Pb[1:].max(), math.log(s), math.log(s2)))
