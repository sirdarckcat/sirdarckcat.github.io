"""GPU & CPU screening for Proth/BLS/Coppersmith Goldbach deserts (v4):
batched 2^((P_t - 1)/2) mod P_t for P_t = m_t * 2^n + 1.

Research Pillar 4A — Feature F17 Part B (`goldbach/proth/gpu_screen_v4.py`):
  1. Algebraic Proth + Cyclic Montgomery Reduction:
     - 1-op carry-free input shift for f in {1, 2}.
     - Proth 2/3-length quotient compression via P == 1 (mod 2^n): bottom L0 = floor(n / W)
       quotient limbs require zero multiplications; upper L1 = L - L0 limbs use K_inv.
     - 1/2-length cyclic Montgomery convolution mod (z^N_cyc - 1) with pre-shifted P_sh
       and exact single-pass Cyclic Kogge-Stone end-around carry lookahead.
  2. Primary GPU Engine (`v4_goldilocks_ntt_graph`):
     - Exact 64-bit Goldilocks prime field p = 2^64 - 2^32 + 1 (zero rounding error!).
     - W = 25-bit limbs -> N_cyc = 16,384 at 16M (304,800b BLS & 272,546b Coppersmith),
       fitting 100% inside 144 KB dynamic shared memory per A100/H100 threadblock.
     - 2 fused kernels per squaring step (`goldilocks_sq_split` + `goldilocks_proth_reduce`)
       using zero-bit-reversal Radix-4 DIF forward / Radix-4 DIT inverse NTTs, plus automatic
       global-memory multi-stage NTT fallback when N_cyc exceeds device shared memory.
  3. Secondary GPU Engine (`v4_proth_cufft_graph`):
     - LIMB = 15 float64 with Proth N_inv (~2/3) + cyclic N_cyc (~1/2) cuFFT `Plan1d`
       transforms and fused scaling / cyclic-fold / Kogge-Stone kernels.
  4. Full-Run Dual CUDA Graph Capture (`graph_head` + `graph_tail`, G = 64 steps/launch):
     - Eliminates ~9,000,000 Python/CUDA host launches per 16M batch.
  5. Zero-GPU Clean Import & Strict Python-Type CPU Reference (`cpu_screen` / `screen_cpu`):
     - Preserves `LIMB = 15`, `to_limbs(vals, L)`, `from_limbs(row)`, `norm15_cpu`.
     - Executes genuine Proth K_inv + Cyclic Kogge-Stone limb arithmetic on CPU (never
       delegating candidate screening to pow/gmpy2.powmod) and returns strict Python
       `list[int]` (or `list[bool]` when `return_bool=True`).
"""
from __future__ import annotations

import math
import sys
from typing import Any

sys.dont_write_bytecode = True
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

import numpy as np

try:
    import gmpy2 as _default_gmpy2  # type: ignore
except ImportError:
    _default_gmpy2 = None

try:
    import cupy as cp  # type: ignore
    import cupy.cuda.cufft as cufft  # type: ignore
    import cupyx.scipy.fft as cfft  # type: ignore
except ImportError:
    cp = None
    cufft = None
    cfft = None

LIMB = 15
MASK = (1 << LIMB) - 1
TILE = 256
HALO = 8

GOLD_P = 0xFFFFFFFF00000001
GOLD_ROOT = 7


def has_gpu() -> bool:
    if cp is None:
        return False
    try:
        return int(cp.cuda.runtime.getDeviceCount()) > 0
    except Exception:
        return False


def _modinv(a: int, m: int) -> int:
    if _default_gmpy2 is not None:
        return int(_default_gmpy2.invert(a, m))
    return pow(int(a), -1, int(m))


def _jacobi_odd(a: int, n: int) -> int:
    """Exact Jacobi symbol (a / n) for odd n >= 3."""
    if _default_gmpy2 is not None:
        return int(_default_gmpy2.jacobi(int(a), int(n)))
    a = int(a) % int(n)
    n = int(n)
    t = 1
    while a != 0:
        while (a & 1) == 0:
            a >>= 1
            r = n & 7
            if r == 3 or r == 5:
                t = -t
        a, n = n, a
        if (a & 3) == 3 and (n & 3) == 3:
            t = -t
        a %= n
    return t if n == 1 else 0


def nice_fft_size(n: int) -> int:
    """Smallest 2^a 3^b 5^c >= n."""
    if n <= 2:
        return 2
    best = 1 << max(1, (n - 1).bit_length())
    p2 = 1
    while p2 < 2 * n:
        p3 = p2
        while p3 < 2 * n:
            p5 = p3
            while p5 < 2 * n:
                if n <= p5 < best:
                    best = p5
                p5 *= 5
            p3 *= 3
        p2 *= 2
    return best


def nice_even_fft_size(n: int) -> int:
    """Smallest even 2 * (2^a 3^b 5^c) >= n (required by cuFFT D2Z / Z2D Plan1d)."""
    return 2 * nice_fft_size(max(2, (int(n) + 1) // 2))


# ---------------------------------------------------------------------------
# Limb Conversion & CPU Carry-Ripple Primitives (Contract #2 / R3-F3)
# ---------------------------------------------------------------------------
def to_limbs(vals: Any, L: int) -> np.ndarray:
    """Python ints (each < 2^(15L)) -> float64 array (len(vals), L) in [0, 0x7FFF]."""
    vals_list = list(vals)
    L_int = int(L)
    if len(vals_list) == 0 or L_int == 0:
        return np.zeros((len(vals_list), L_int), dtype=np.float64)
    nbytes = (LIMB * L_int + 7) // 8 + 1
    w = (1 << np.arange(LIMB, dtype=np.int64))
    limit = 1 << (LIMB * L_int)
    out = np.empty((len(vals_list), L_int), dtype=np.float64)
    for j, v_raw in enumerate(vals_list):
        v = int(v_raw)
        assert 0 <= v < limit, "value does not fit in L limbs"
        b = np.frombuffer(v.to_bytes(nbytes, "little"), dtype=np.uint8)
        bits = np.unpackbits(b, bitorder="little")[: LIMB * L_int]
        out[j] = bits.reshape(L_int, LIMB).astype(np.int64) @ w
    return out


def from_limbs(row: Any) -> int:
    """Normalised limb row (float64/int) -> strict Python int."""
    arr = np.asarray(row, dtype=np.float64)
    if arr.size == 0:
        return 0
    limbs = np.rint(arr).astype(np.int64)
    assert int(limbs.min()) >= 0 and int(limbs.max()) <= MASK, "row not normalised"
    acc = 0
    for v in reversed(limbs.tolist()):
        acc = (acc << LIMB) | int(v)
    return int(acc)


def to_limbs_u32(vals: Any, L: int, W: int = 25) -> np.ndarray:
    """Python ints -> uint32 array (len(vals), L) in [0, (1 << W) - 1]."""
    vals_list = list(vals)
    L_int, W_int = int(L), int(W)
    if len(vals_list) == 0 or L_int == 0:
        return np.zeros((len(vals_list), L_int), dtype=np.uint32)
    mask_w = (1 << W_int) - 1
    limit = 1 << (W_int * L_int)
    if W_int == 25:
        n_blk = (L_int + 7) // 8
        nbytes = 25 * n_blk
        pad_out = np.empty((len(vals_list), 8 * n_blk), dtype=np.uint32)
        for j, v_raw in enumerate(vals_list):
            v = int(v_raw)
            assert 0 <= v < limit, "value does not fit in L limbs"
            b = np.frombuffer(v.to_bytes(nbytes, "little"), dtype=np.uint8).reshape(n_blk, 25).astype(np.uint32)
            row = pad_out[j].reshape(n_blk, 8)
            row[:, 0] = (b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16) | (b[:, 3] << 24)) & 0x1FFFFFF
            row[:, 1] = ((b[:, 3] >> 1) | (b[:, 4] << 7) | (b[:, 5] << 15) | (b[:, 6] << 23)) & 0x1FFFFFF
            row[:, 2] = ((b[:, 6] >> 2) | (b[:, 7] << 6) | (b[:, 8] << 14) | (b[:, 9] << 22)) & 0x1FFFFFF
            row[:, 3] = ((b[:, 9] >> 3) | (b[:, 10] << 5) | (b[:, 11] << 13) | (b[:, 12] << 21)) & 0x1FFFFFF
            row[:, 4] = ((b[:, 12] >> 4) | (b[:, 13] << 4) | (b[:, 14] << 12) | (b[:, 15] << 20)) & 0x1FFFFFF
            row[:, 5] = ((b[:, 15] >> 5) | (b[:, 16] << 3) | (b[:, 17] << 11) | (b[:, 18] << 19)) & 0x1FFFFFF
            row[:, 6] = ((b[:, 18] >> 6) | (b[:, 19] << 2) | (b[:, 20] << 10) | (b[:, 21] << 18)) & 0x1FFFFFF
            row[:, 7] = (b[:, 21] >> 7) | (b[:, 22] << 1) | (b[:, 23] << 9) | (b[:, 24] << 17)
        return np.ascontiguousarray(pad_out[:, :L_int])

    out = np.zeros((len(vals_list), L_int), dtype=np.uint32)
    for j, v_raw in enumerate(vals_list):
        v = int(v_raw)
        assert 0 <= v < limit, "value does not fit in L limbs"
        idx = 0
        while v > 0 and idx < L_int:
            out[j, idx] = v & mask_w
            v >>= W_int
            idx += 1
    return out


def from_limbs_u32(row: Any, W: int = 25) -> int:
    """Normalised uint32/int limb row -> strict Python int."""
    arr = np.asarray(row, dtype=np.int64)
    if arr.size == 0:
        return 0
    mask_w = (1 << int(W)) - 1
    assert int(arr.min()) >= 0 and int(arr.max()) <= mask_w, "row not normalised"
    acc = 0
    W_int = int(W)
    for v in reversed(arr.tolist()):
        acc = (acc << W_int) | int(v)
    return int(acc)


def norm_linear_cpu(raw_2d: np.ndarray, W: int = 15, n_dst: int | None = None) -> np.ndarray:
    """Exact CPU simulation of multi-round local carry + Kogge-Stone linear carry lookahead
    truncating modulo 2^(W * n_dst). Handles arbitrary-length (1<<W)-1 carry ripples.
    """
    arr = np.asarray(raw_2d)
    if arr.ndim == 1:
        return norm_linear_cpu(arr[None, :], W=W, n_dst=n_dst)[0]
    B, n_src = arr.shape
    L_out = int(n_src if n_dst is None else n_dst)
    out_dtype = np.float64 if W == 15 else np.uint32
    if B == 0 or L_out == 0:
        return np.zeros((B, L_out), dtype=out_dtype)

    mask_u = np.uint64((1 << W) - 1)
    w_u = np.uint64(W)
    w2_u = np.uint64(2 * W)
    if np.issubdtype(arr.dtype, np.unsignedinteger):
        ints = arr.astype(np.uint64)
    elif np.issubdtype(arr.dtype, np.floating):
        ints = np.maximum(0.0, np.rint(arr)).astype(np.uint64)
    else:
        ints = arr.astype(np.uint64)

    # 1. Vectorized 4-limb gather + 4 local carry rounds (exact unsigned 64-bit mirror of GPU normalizers)
    lim = min(n_src, L_out)
    z = np.zeros((B, L_out), dtype=np.uint64)
    z[:, :lim] = ints[:, :lim] & mask_u
    if lim > 1:
        z[:, 1:lim] += (ints[:, : lim - 1] >> w_u) & mask_u
    elif L_out > 1 and n_src >= 1:
        z[:, 1] += (ints[:, 0] >> w_u) & mask_u
    if L_out > 2 and n_src >= 1:
        end2 = min(L_out, n_src + 1)
        z[:, 2:end2] += (ints[:, : end2 - 2] >> w2_u) & mask_u
    if 3 * W < 64 and L_out > 3 and n_src >= 1:
        w3_u = np.uint64(3 * W)
        end3 = min(L_out, n_src + 2)
        z[:, 3:end3] += ints[:, : end3 - 3] >> w3_u

    for _ in range(4):
        carries = z[:, :-1] >> w_u
        z &= mask_u
        if L_out > 1:
            z[:, 1:] += carries

    # 2. Vectorized Kogge-Stone carry-lookahead on any flagged rows (0x7FFF / MASK runs)
    lim_u = np.uint64(1 << W)
    flagged = np.where(np.any(z >= lim_u, axis=1))[0]
    if flagged.size > 0:
        zf = z[flagged]
        Gf = (zf >= lim_u).astype(np.uint8)
        Pf = (zf == mask_u).astype(np.uint8)
        off = 1
        while off < L_out:
            Gf[:, off:] |= Pf[:, off:] & Gf[:, :-off]
            Pf[:, off:] &= Pf[:, :-off]
            off <<= 1
        cin = np.zeros_like(Gf, dtype=np.uint64)
        if L_out > 1:
            cin[:, 1:] = Gf[:, :-1]
        z[flagged] = ((zf & mask_u) + cin) & mask_u

    return z.astype(out_dtype)


def norm15_cpu(arr: np.ndarray, n_dst: int | None = None) -> np.ndarray:
    """Exact LIMB=15 CPU linear carry normalizer."""
    return norm_linear_cpu(arr, W=LIMB, n_dst=n_dst)


def resolve_cyclic_cpu(c_prime_row: list[int] | np.ndarray, W: int = 25) -> list[int]:
    """Exact CPU implementation of 4-round cyclic carry + Single-Pass Cyclic Kogge-Stone
    modulo (2^(W * N_cyc) - 1). Handles 66-bit inputs and full-ring MASK wraparounds.
    """
    vals = [int(x) for x in c_prime_row]
    N_cyc = len(vals)
    mask_w = (1 << W) - 1

    # Round 1: exact arbitrary-bit cyclic split across k, k-1, k-2
    z = [0] * N_cyc
    for k in range(N_cyc):
        v = vals[k] & mask_w
        c1 = (vals[(k - 1) % N_cyc] >> W) & mask_w
        c2 = vals[(k - 2) % N_cyc] >> (2 * W)
        z[k] = v + c1 + c2

    # Rounds 2..5: reduce every entry into [0, 1 << W]
    for _ in range(4):
        nxt = [0] * N_cyc
        for k in range(N_cyc):
            nxt[k] = (z[k] & mask_w) + (z[(k - 1) % N_cyc] >> W)
        z = nxt

    T_seg = min(64, max(1, N_cyc))
    seg = (N_cyc + T_seg - 1) // T_seg
    G = [0] * T_seg
    Pp = [1] * T_seg
    for tid in range(T_seg):
        lo_i = tid * seg
        hi_i = min(N_cyc, lo_i + seg)
        g, p = 0, 1
        for i in range(lo_i, hi_i):
            vi = z[i]
            gi = 1 if vi >= (1 << W) else 0
            pi = 1 if vi == mask_w else 0
            g = gi | (pi & g)
            p = pi & p
        G[tid] = g
        Pp[tid] = p

    off = 1
    while off < T_seg:
        Gn = list(G)
        Pn = list(Pp)
        for tid in range(off, T_seg):
            Gn[tid] = G[tid] | (Pp[tid] & G[tid - off])
            Pn[tid] = Pp[tid] & Pp[tid - off]
        G, Pp = Gn, Pn
        off <<= 1

    c_wrap = G[T_seg - 1]
    all_mask = Pp[T_seg - 1]
    if all_mask and not c_wrap:
        return [0] * N_cyc

    out = [0] * N_cyc
    for tid in range(T_seg):
        lo_i = tid * seg
        hi_i = min(N_cyc, lo_i + seg)
        c = c_wrap if tid == 0 else (G[tid - 1] | (Pp[tid - 1] & c_wrap))
        for i in range(lo_i, hi_i):
            v = z[i] + c
            c = v >> W
            out[i] = v & mask_w
    return out


# ---------------------------------------------------------------------------
# CPU Exact Goldilocks Radix-4 DIF / DIT & Genuine Proth Reference Engine
# ---------------------------------------------------------------------------
def _choose_goldilocks_params(bits: int, n: int) -> tuple[int, int, int, int, int, int]:
    """Select (W, L_P, L, L0, L1, N_cyc) guaranteeing L * (2^W - 1)^2 < GOLD_P and N_cyc >= max(L+2, 2*L1)."""
    for W in range(25, 14, -1):
        L_P = (int(bits) + W - 1) // W
        L = L_P + 2
        if L * ((1 << W) - 1) ** 2 < GOLD_P - (1 << 40):
            L0 = int(n) // W
            L1 = L - L0
            need = max(L + 2, 2 * L1)
            lgN = max(6, (need - 1).bit_length())
            N_cyc = 1 << lgN
            return W, L_P, L, L0, L1, N_cyc
    raise ValueError(f"Candidate bit-width {bits} exceeds 64-bit Goldilocks single-prime convolution bound")


def _build_goldilocks_tables(N_cyc: int) -> dict[str, np.ndarray | int]:
    """Precompute Radix-4 DIF/DIT twiddle triples and negacyclic twist tables in F_p."""
    lgN = (N_cyc - 1).bit_length()
    assert (1 << lgN) == N_cyc
    g_root = pow(GOLD_ROOT, (GOLD_P - 1) // N_cyc, GOLD_P)
    psi = pow(GOLD_ROOT, (GOLD_P - 1) // (2 * N_cyc), GOLD_P)
    inv_psi = pow(psi, -1, GOLD_P)
    inv_N = pow(N_cyc, -1, GOLD_P)

    psi_pows = np.empty(N_cyc, dtype=np.uint64)
    inv_psi_n = np.empty(N_cyc, dtype=np.uint64)
    cur_p = 1
    cur_ip = inv_N
    for i in range(N_cyc):
        psi_pows[i] = cur_p
        inv_psi_n[i] = cur_ip
        cur_p = (cur_p * psi) % GOLD_P
        cur_ip = (cur_ip * inv_psi) % GOLD_P

    m_stages: list[int] = []
    m_cur = N_cyc
    while m_cur >= 4:
        m_stages.append(m_cur)
        m_cur >>= 2

    dif_list: list[int] = []
    for m_st in m_stages:
        q = m_st >> 2
        step = N_cyc // m_st
        w_step = pow(g_root, step, GOLD_P)
        w1 = 1
        for _ in range(q):
            w2 = (w1 * w1) % GOLD_P
            w3 = (w2 * w1) % GOLD_P
            dif_list.extend((w1, w2, w3))
            w1 = (w1 * w_step) % GOLD_P

    dit_list: list[int] = []
    for m_st in reversed(m_stages):
        q = m_st >> 2
        step = N_cyc // m_st
        iw_step = pow(pow(g_root, step, GOLD_P), -1, GOLD_P)
        iw1 = 1
        for _ in range(q):
            iw2 = (iw1 * iw1) % GOLD_P
            iw3 = (iw2 * iw1) % GOLD_P
            dit_list.extend((iw1, iw2, iw3))
            iw1 = (iw1 * iw_step) % GOLD_P

    return {
        "N_cyc": N_cyc,
        "lgN": lgN,
        "inv_N": inv_N,
        "psi_pows": psi_pows,
        "inv_psi_n": inv_psi_n,
        "dif_tw": np.asarray(dif_list, dtype=np.uint64),
        "dit_tw": np.asarray(dit_list, dtype=np.uint64),
    }


def ntt_dif_goldilocks_cpu(vec: np.ndarray, tabs: dict[str, Any]) -> list[int]:
    """Exact CPU Radix-4 DIF forward NTT over F_p (zero bit-reversal)."""
    N = int(tabs["N_cyc"])
    lgN = int(tabs["lgN"])
    dif_tw = tabs["dif_tw"].tolist()
    s = [int(x) % GOLD_P for x in vec]
    w4 = 1 << 48
    tw_base = 0
    m = N
    while m >= 4:
        q = m >> 2
        for idx in range(N >> 2):
            j = idx & (q - 1)
            base = (idx ^ j) << 2
            a0, a1, a2, a3 = s[base + j], s[base + j + q], s[base + j + 2 * q], s[base + j + 3 * q]
            t0 = (a0 + a2) % GOLD_P
            t1 = (a1 + a3) % GOLD_P
            t2 = (a0 - a2) % GOLD_P
            t3 = ((a1 - a3) * w4) % GOLD_P
            y0 = (t0 + t1) % GOLD_P
            y1 = (t2 + t3) % GOLD_P
            y2 = (t0 - t1) % GOLD_P
            y3 = (t2 - t3) % GOLD_P
            if j != 0:
                toff = (tw_base + j) * 3
                y1 = (y1 * dif_tw[toff]) % GOLD_P
                y2 = (y2 * dif_tw[toff + 1]) % GOLD_P
                y3 = (y3 * dif_tw[toff + 2]) % GOLD_P
            s[base + j], s[base + j + q], s[base + j + 2 * q], s[base + j + 3 * q] = y0, y1, y2, y3
        tw_base += q
        m >>= 2
    if lgN & 1:
        for idx in range(N >> 1):
            b = idx << 1
            a0, a1 = s[b], s[b + 1]
            s[b], s[b + 1] = (a0 + a1) % GOLD_P, (a0 - a1) % GOLD_P
    return s


def intt_dit_goldilocks_cpu(vec: list[int] | np.ndarray, tabs: dict[str, Any]) -> list[int]:
    """Exact CPU Radix-4 DIT inverse NTT over F_p (returns N * x mod GOLD_P)."""
    N = int(tabs["N_cyc"])
    lgN = int(tabs["lgN"])
    dit_tw = tabs["dit_tw"].tolist()
    s = [int(x) % GOLD_P for x in vec]
    w4 = 1 << 48
    if lgN & 1:
        for idx in range(N >> 1):
            b = idx << 1
            a0, a1 = s[b], s[b + 1]
            s[b], s[b + 1] = (a0 + a1) % GOLD_P, (a0 - a1) % GOLD_P
    tw_base = 0
    m = 8 if (lgN & 1) else 4
    while m <= N:
        q = m >> 2
        for idx in range(N >> 2):
            j = idx & (q - 1)
            base = (idx ^ j) << 2
            z0, z1, z2, z3 = s[base + j], s[base + j + q], s[base + j + 2 * q], s[base + j + 3 * q]
            if j != 0:
                toff = (tw_base + j) * 3
                z1 = (z1 * dit_tw[toff]) % GOLD_P
                z2 = (z2 * dit_tw[toff + 1]) % GOLD_P
                z3 = (z3 * dit_tw[toff + 2]) % GOLD_P
            u0 = (z0 + z2) % GOLD_P
            u1 = (z1 + z3) % GOLD_P
            u2 = (z0 - z2) % GOLD_P
            u3 = ((z3 - z1) * w4) % GOLD_P
            s[base + j] = (u0 + u1) % GOLD_P
            s[base + j + q] = (u2 + u3) % GOLD_P
            s[base + j + 2 * q] = (u0 - u1) % GOLD_P
            s[base + j + 3 * q] = (u2 - u3) % GOLD_P
        tw_base += q
        m <<= 2
    return s


def _cpu_cyclic_conv_exact(a: np.ndarray, b: np.ndarray, N_cyc: int) -> np.ndarray:
    """Exact integer cyclic convolution (a (*) b) mod (z^N_cyc - 1) via float64 split-13b FFT
    (zero modular wrap, O(N log N) speed for fast multi-thousand-step CPU validation).
    """
    # Split <= 25-bit limbs into 13-bit lo + 12-bit hi in unsigned uint64 (exact < 2^64 up to 304,800b+)
    a64 = np.asarray(a, dtype=np.uint64)
    b64 = np.asarray(b, dtype=np.uint64)
    a0 = (a64 & np.uint64(0x1FFF)).astype(np.float64)
    a1 = (a64 >> np.uint64(13)).astype(np.float64)
    b0 = (b64 & np.uint64(0x1FFF)).astype(np.float64)
    b1 = (b64 >> np.uint64(13)).astype(np.float64)

    fa0 = np.fft.rfft(a0, n=N_cyc, axis=-1)
    fa1 = np.fft.rfft(a1, n=N_cyc, axis=-1)
    fb0 = np.fft.rfft(b0, n=N_cyc, axis=-1)
    fb1 = np.fft.rfft(b1, n=N_cyc, axis=-1)

    c0 = np.maximum(0.0, np.rint(np.fft.irfft(fa0 * fb0, n=N_cyc, axis=-1))).astype(np.uint64)
    c1 = np.maximum(0.0, np.rint(np.fft.irfft(fa0 * fb1 + fa1 * fb0, n=N_cyc, axis=-1))).astype(np.uint64)
    c2 = np.maximum(0.0, np.rint(np.fft.irfft(fa1 * fb1, n=N_cyc, axis=-1))).astype(np.uint64)
    return c0 + (c1 << np.uint64(13)) + (c2 << np.uint64(26))


class ProthCPUEngine:
    """Genuine CPU Proth Montgomery screener executing exact W-bit Proth K_inv quotient
    compression + 1/2-length cyclic Montgomery reduction + Cyclic Kogge-Stone carry lookahead.
    """

    def __init__(self, n: int, ms: list[int], *, engine: str = "proth_ntt"):
        self.n = int(n)
        self.ms = [int(m) for m in ms]
        self.P = [(m << self.n) + 1 for m in self.ms]
        self.B = len(self.P)
        self.engine = engine

        bits = max(p.bit_length() for p in self.P)
        if engine == "proth_cufft":
            self.W = 15
            self.L = (bits + 5 + 14) // 15
            self.L0 = self.n // 15
            self.L1 = self.L - self.L0
            self.N_cyc = nice_even_fft_size(self.L + 4)
            self.N_sq = max(self.N_cyc, nice_even_fft_size(2 * self.L + 2))
            self.N_inv = nice_even_fft_size(2 * self.L1 + 2)
        else:
            self.W, _, self.L, self.L0, self.L1, self.N_cyc = _choose_goldilocks_params(bits, self.n)
            self.N_sq = 2 * self.N_cyc
            self.N_inv = self.N_cyc

        self.mask_w = (1 << self.W) - 1
        self.R = 1 << (self.W * self.L)
        B_L0 = 1 << (self.W * self.L0)
        B_L1 = 1 << (self.W * self.L1)

        K_invs: list[int] = []
        self.x0_ints: list[int] = []
        for p in self.P:
            pinv = (-_modinv(p, self.R)) % self.R
            assert (pinv + 1) % B_L0 == 0
            kinv = ((pinv + 1) // B_L0) % B_L1
            K_invs.append(kinv)
            self.x0_ints.append(self.R % p)

        self.Kinv_limbs = to_limbs_u32(K_invs, self.L1, W=self.W).astype(np.uint64)
        P_limbs = to_limbs_u32(self.P, self.L, W=self.W).astype(np.uint64)
        self.P_sh = np.zeros((self.B, self.N_cyc), dtype=np.uint64)
        for k in range(self.L):
            self.P_sh[:, (k - self.L) % self.N_cyc] = P_limbs[:, k]

        # Single float64 FFT is restricted strictly to W <= 15 with L^2 * (2^W - 1)^2 < 2^48;
        # all W > 15 (proth_ntt) and larger L use split-13b exact FFT.
        self._single_f64 = (self.W <= 15) and ((self.L ** 2) * ((1 << self.W) - 1) ** 2 < (1 << 48))
        kinv_pad = np.zeros((self.B, self.N_inv), dtype=np.uint64)
        kinv_pad[:, : self.L1] = self.Kinv_limbs
        if self._single_f64:
            self._fkinv_0 = np.fft.rfft(kinv_pad.astype(np.float64), n=self.N_inv, axis=-1)
            self._fkinv_1 = None
            self._fpsh_0 = np.fft.rfft(self.P_sh.astype(np.float64), n=self.N_cyc, axis=-1)
            self._fpsh_1 = None
        else:
            self._fkinv_0 = np.fft.rfft((kinv_pad & np.uint64(0x1FFF)).astype(np.float64), n=self.N_inv, axis=-1)
            self._fkinv_1 = np.fft.rfft((kinv_pad >> np.uint64(13)).astype(np.float64), n=self.N_inv, axis=-1)
            self._fpsh_0 = np.fft.rfft((self.P_sh & np.uint64(0x1FFF)).astype(np.float64), n=self.N_cyc, axis=-1)
            self._fpsh_1 = np.fft.rfft((self.P_sh >> np.uint64(13)).astype(np.float64), n=self.N_cyc, axis=-1)

        self._fold_j0 = (self.L + np.arange(self.N_cyc)) % self.N_cyc

        self.K0 = max(m.bit_length() for m in self.ms)
        mb = np.zeros((self.B, self.K0), dtype=np.uint8)
        for j, m in enumerate(self.ms):
            s = bin(m)[2:]
            mb[j, self.K0 - len(s) :] = [1 if ch == "1" else 0 for ch in s]
        self.mbits = np.ascontiguousarray(mb.T)

        self._gold_tabs = _build_goldilocks_tables(self.N_cyc) if (engine == "goldilocks_exact_radix4") else None

    def _conv_with_pre(self, a_pad: np.ndarray, fb0: np.ndarray, fb1: np.ndarray | None, N_len: int) -> np.ndarray:
        a_u64 = np.asarray(a_pad, dtype=np.uint64)
        if self._single_f64:
            fa = np.fft.rfft(a_u64.astype(np.float64), n=N_len, axis=-1)
            return np.maximum(0.0, np.rint(np.fft.irfft(fa * fb0, n=N_len, axis=-1))).astype(np.uint64)
        assert fb1 is not None
        fa0 = np.fft.rfft((a_u64 & np.uint64(0x1FFF)).astype(np.float64), n=N_len, axis=-1)
        fa1 = np.fft.rfft((a_u64 >> np.uint64(13)).astype(np.float64), n=N_len, axis=-1)
        c0 = np.maximum(0.0, np.rint(np.fft.irfft(fa0 * fb0, n=N_len, axis=-1))).astype(np.uint64)
        c1 = np.maximum(0.0, np.rint(np.fft.irfft(fa0 * fb1 + fa1 * fb0, n=N_len, axis=-1))).astype(np.uint64)
        c2 = np.maximum(0.0, np.rint(np.fft.irfft(fa1 * fb1, n=N_len, axis=-1))).astype(np.uint64)
        return c0 + (c1 << np.uint64(13)) + (c2 << np.uint64(26))

    def mont_sq_step(self, x_limbs: np.ndarray, f_vec: np.ndarray) -> np.ndarray:
        """Execute 1 Proth + Cyclic Montgomery squaring step (f_vec[r] in {1, 2})."""
        B, L, L0, L1, W, mask_w = self.B, self.L, self.L0, self.L1, self.W, self.mask_w
        N_cyc = self.N_cyc
        mask_u = np.uint64(mask_w)
        w_u = np.uint64(W)

        # 1. Vectorized carry-free shift y = f * x
        y = np.asarray(x_limbs, dtype=np.uint64).copy()
        dbl = np.asarray(f_vec) == 2
        if np.any(dbl):
            xd = y[dbl]
            yd = (xd << np.uint64(1)) & mask_u
            if L > 1:
                yd[:, 1:] |= xd[:, :-1] >> np.uint64(W - 1)
            y[dbl] = yd

        # 2. Exact squaring T = y^2 in unsigned uint64 (< GOLD_P < 2^64)
        if self._gold_tabs is not None:
            tabs = self._gold_tabs
            inv_N = int(tabs["inv_N"])
            psi_p = tabs["psi_pows"]
            inv_psi_n = tabs["inv_psi_n"]
            half_p = (GOLD_P + 1) >> 1
            T_raw = np.zeros((B, 2 * N_cyc), dtype=np.uint64)
            for r in range(B):
                ypad = [int(x) for x in y[r]] + [0] * (N_cyc - L)
                ntt_p = ntt_dif_goldilocks_cpu(ypad, tabs)
                sp = [(v * inv_N) % GOLD_P for v in intt_dit_goldilocks_cpu([(u * u) % GOLD_P for u in ntt_p], tabs)]
                ytw = [(ypad[i] * int(psi_p[i])) % GOLD_P for i in range(N_cyc)]
                ntt_m = ntt_dif_goldilocks_cpu(ytw, tabs)
                sm_raw = intt_dit_goldilocks_cpu([(u * u) % GOLD_P for u in ntt_m], tabs)
                sm = [(sm_raw[i] * int(inv_psi_n[i])) % GOLD_P for i in range(N_cyc)]
                for i in range(N_cyc):
                    T_raw[r, i] = np.uint64((((sp[i] + sm[i]) % GOLD_P) * half_p) % GOLD_P)
                    T_raw[r, i + N_cyc] = np.uint64((((sp[i] - sm[i]) % GOLD_P) * half_p) % GOLD_P)
        elif self._single_f64:
            fy = np.fft.rfft(y.astype(np.float64), n=self.N_sq, axis=-1)
            T_raw = np.maximum(0.0, np.rint(np.fft.irfft(fy * fy, n=self.N_sq, axis=-1))).astype(np.uint64)
        else:
            fy0 = np.fft.rfft((y & np.uint64(0x1FFF)).astype(np.float64), n=self.N_sq, axis=-1)
            fy1 = np.fft.rfft((y >> np.uint64(13)).astype(np.float64), n=self.N_sq, axis=-1)
            c0 = np.maximum(0.0, np.rint(np.fft.irfft(fy0 * fy0, n=self.N_sq, axis=-1))).astype(np.uint64)
            c1 = np.maximum(0.0, np.rint(np.fft.irfft(2.0 * fy0 * fy1, n=self.N_sq, axis=-1))).astype(np.uint64)
            c2 = np.maximum(0.0, np.rint(np.fft.irfft(fy1 * fy1, n=self.N_sq, axis=-1))).astype(np.uint64)
            T_raw = c0 + (c1 << np.uint64(13)) + (c2 << np.uint64(26))

        # 3. Linear carry normalize T_lo = T mod R
        T_lo = norm_linear_cpu(T_raw[:, :L], W=W, n_dst=L).astype(np.uint64)

        # 4. Proth 2/3-length quotient m1 = (T_lo[:L1] * K_inv) mod B_limb^L1
        m1_raw = self._conv_with_pre(T_lo[:, :L1], self._fkinv_0, self._fkinv_1, self.N_inv)
        m1 = norm_linear_cpu(m1_raw[:, :L1], W=W, n_dst=L1).astype(np.uint64)

        q_raw = mask_u - T_lo
        q_raw[:, 0] += np.uint64(1)
        q_raw[:, L0:L] += m1
        q = norm_linear_cpu(q_raw, W=W, n_dst=L).astype(np.uint64)

        # 5. Half-length cyclic product q (*) P_sh mod (z^N_cyc - 1)
        qp_sh = self._conv_with_pre(q, self._fpsh_0, self._fpsh_1, N_cyc)

        # 6. Exact 96-bit (c_lo, c_hi) cyclic fold (matching GPU goldilocks_proth_reduce) + Kogge-Stone
        j0 = self._fold_j0
        t0 = T_raw[:, j0]
        with np.errstate(over="ignore"):
            c_lo = t0 + qp_sh
        c_hi = (c_lo < t0).astype(np.uint64)

        j1 = j0 + N_cyc
        valid_j1 = j1 < T_raw.shape[1]
        if np.any(valid_j1):
            t1 = T_raw[:, j1[valid_j1]]
            prev_lo = c_lo[:, valid_j1]
            with np.errstate(over="ignore"):
                new_lo = prev_lo + t1
            c_hi[:, valid_j1] += (new_lo < prev_lo).astype(np.uint64)
            c_lo[:, valid_j1] = new_lo

        v0 = c_lo & mask_u
        m1_lo = np.roll(c_lo, 1, axis=1)
        m1_hi = np.roll(c_hi, 1, axis=1)
        c1 = ((m1_lo >> w_u) | (m1_hi << np.uint64(64 - W))) & mask_u
        m2_lo = np.roll(c_lo, 2, axis=1)
        m2_hi = np.roll(c_hi, 2, axis=1)
        w2_u = np.uint64(2 * W)
        if 3 * W >= 66:
            c2 = (m2_lo >> w2_u) | (m2_hi << np.uint64(64 - 2 * W))
            z = v0 + c1 + c2
        else:
            c2 = ((m2_lo >> w2_u) | (m2_hi << np.uint64(64 - 2 * W))) & mask_u
            m3_lo = np.roll(c_lo, 3, axis=1)
            m3_hi = np.roll(c_hi, 3, axis=1)
            c3 = (m3_lo >> np.uint64(3 * W)) | (m3_hi << np.uint64(64 - 3 * W))
            z = v0 + c1 + c2 + c3

        for _ in range(4):
            z = (z & mask_u) + (np.roll(z, 1, axis=1) >> w_u)

        lim_u = np.uint64(1 << W)
        flagged = np.where(np.any(z >= lim_u, axis=1) | np.all(z == mask_u, axis=1))[0]
        if flagged.size > 0:
            zf = z[flagged]
            Gf = (zf >= lim_u).astype(np.uint8)
            Pf = (zf == mask_u).astype(np.uint8)
            off = 1
            while off < N_cyc:
                Gf = Gf | (Pf & np.roll(Gf, off, axis=1))
                Pf = Pf & np.roll(Pf, off, axis=1)
                off <<= 1
            res_f = ((zf & mask_u) + np.roll(Gf, 1, axis=1).astype(np.uint64)) & mask_u
            res_f[np.all(res_f == mask_u, axis=1)] = np.uint64(0)
            z[flagged] = res_f

        assert not bool(np.any(z[:, L:] != 0)), "non-zero upper cyclic Montgomery limbs!"
        return z[:, :L].astype(np.int64)

    def run(self) -> list[int]:
        """Run full 2^((P_j - 1)/2) mod P_j exponentiation on CPU, returning strict list[int]."""
        x = to_limbs_u32(self.x0_ints, self.L, W=self.W).astype(np.int64)
        f = np.ones(self.B, dtype=np.int64)
        ones = np.ones(self.B, dtype=np.int64)
        K = self.K0 + self.n - 1
        for k in range(K):
            x = self.mont_sq_step(x, f)
            if k < self.K0:
                f = 1 + self.mbits[k].astype(np.int64)
            else:
                f = ones
        out: list[int] = []
        for j, p in enumerate(self.P):
            v_mont = (from_limbs_u32(x[j], W=self.W) * int(f[j])) % p
            r_val = int((v_mont * _modinv(self.R, p)) % p)
            out.append(r_val)
        return out


def _limb_mont_pow_general_cpu(base: int, exp: int, mod_p: int) -> int:
    """Limb-based Montgomery modular exponentiation for non-base-2 fallback (no pow(b,e,m) shortcut)."""
    W = 25
    L = (mod_p.bit_length() + W - 1) // W + 2
    R = 1 << (W * L)
    mask_w = (1 << W) - 1
    p_inv0 = (-_modinv(mod_p, 1 << W)) & mask_w
    p_limbs = to_limbs_u32([mod_p], L, W=W)[0].tolist()

    def mont_mul(a_l: list[int], b_l: list[int]) -> list[int]:
        t = [0] * (L + 2)
        for i in range(L):
            ai = a_l[i]
            if ai:
                c = 0
                for j in range(L):
                    s = t[j] + ai * b_l[j] + c
                    t[j] = s & mask_w
                    c = s >> W
                t[L] += c
            q0 = (t[0] * p_inv0) & mask_w
            c = (t[0] + q0 * p_limbs[0]) >> W
            for j in range(1, L):
                s = t[j] + q0 * p_limbs[j] + c
                t[j - 1] = s & mask_w
                c = s >> W
            s_top = t[L] + c
            t[L - 1] = s_top & mask_w
            t[L] = (s_top >> W) + t[L + 1]
            t[L + 1] = 0
        return t[:L]

    acc = to_limbs_u32([R % mod_p], L, W=W)[0].tolist()
    b_m = to_limbs_u32([(int(base) * R) % mod_p], L, W=W)[0].tolist()
    for bit in bin(int(exp))[2:]:
        acc = mont_mul(acc, acc)
        if bit == "1":
            acc = mont_mul(acc, b_m)
    one_l = [1] + [0] * (L - 1)
    res_l = mont_mul(acc, one_l)
    val = from_limbs_u32(res_l, W=W)
    while val >= mod_p:
        val -= mod_p
    return int(val)


def cpu_screen(
    ps_or_n: Any,
    ms: Any = None,
    *,
    base: int = 2,
    return_bool: bool = False,
    engine: str = "proth_ntt",
) -> list[int] | list[bool]:
    """Genuine CPU bit-exact reference screener for Proth candidates.

    Calling forms:
      - cpu_screen(ps): `ps` is an iterable of odd integers P_j >= 3.
      - cpu_screen(n, ms): P_j = (m_j << n) + 1.

    Returns strict Python `list[int]` (`type(x) is int`) by default, or
    `list[bool]` (`type(x) is bool`) when `return_bool=True`.
    """
    base_int = int(base)
    if ms is not None:
        n_int = int(ps_or_n)
        ms_list = [int(m) for m in ms]
        ps_list = [(m << n_int) + 1 for m in ms_list]
        if len(ms_list) == 0:
            return []
        if base_int == 2 and n_int >= 1:
            residues = ProthCPUEngine(n_int, ms_list, engine=engine).run()
        else:
            residues = [_limb_mont_pow_general_cpu(base_int, (p - 1) >> 1, p) for p in ps_list]
    else:
        ps_list = [int(p) for p in ps_or_n]
        if len(ps_list) == 0:
            return []
        residues = [0] * len(ps_list)
        groups: dict[int, list[tuple[int, int]]] = {}
        for idx, p in enumerate(ps_list):
            if p < 3 or (p & 1) == 0:
                raise ValueError(f"Proth candidate P={p} must be odd >= 3")
            pm1 = p - 1
            v2 = (pm1 & -pm1).bit_length() - 1
            if base_int == 2 and v2 >= 1:
                groups.setdefault(v2, []).append((idx, pm1 >> v2))
            else:
                residues[idx] = _limb_mont_pow_general_cpu(base_int, pm1 >> 1, p)
        for v2, items in groups.items():
            sub_ms = [m for _, m in items]
            sub_res = ProthCPUEngine(v2, sub_ms, engine=engine).run()
            for (orig_idx, _), r_val in zip(items, sub_res):
                residues[orig_idx] = int(r_val)

    if return_bool:
        out_b: list[bool] = []
        for p, r in zip(ps_list, residues):
            j_sym = _jacobi_odd(base_int, p)
            target = 1 if j_sym == 1 else (p - 1 if j_sym == -1 else -1)
            out_b.append(bool(int(r) == target))
        return out_b
    return [int(r) for r in residues]


screen_cpu = cpu_screen


# ---------------------------------------------------------------------------
# CUDA C++ Sources for Engine 1 (`v4_goldilocks_ntt_graph`) & Engine 2 (`v4_proth_cufft_graph`)
# ---------------------------------------------------------------------------
_GOLDILOCKS_CUDA_SRC = r"""
using u64_t = unsigned long long;
using u32_t = unsigned int;
using u8_t  = unsigned char;

static constexpr u64_t GOLD_P     = 0xFFFFFFFF00000001ULL;
static constexpr u64_t GOLD_EPS32 = 0xFFFFFFFFULL;
static constexpr u64_t GOLD_HALF  = 0x7FFFFFFF80000001ULL;

__device__ __forceinline__ u64_t gold_add(u64_t a, u64_t b) {
    u64_t s = a + b;
    if ((s < a) || (s >= GOLD_P)) s += GOLD_EPS32;
    return s;
}

__device__ __forceinline__ u64_t gold_sub(u64_t a, u64_t b) {
    u64_t d = a - b;
    if (a < b) d -= GOLD_EPS32;
    return d;
}

__device__ __forceinline__ u64_t gold_mul(u64_t a, u64_t b) {
    u64_t lo = a * b;
    u64_t hi = __umul64hi(a, b);
    u64_t hi_lo = (u32_t)hi;
    u64_t hi_hi = hi >> 32;
    u64_t t0 = lo - hi_hi;
    if (lo < hi_hi) t0 -= GOLD_EPS32;
    else if (t0 >= GOLD_P) t0 -= GOLD_P;
    u64_t t1 = (hi_lo << 32) - hi_lo;
    u64_t s = t0 + t1;
    if ((s < t0) || (s >= GOLD_P)) s += GOLD_EPS32;
    return s;
}

__device__ __forceinline__ u64_t gold_mul_2pow48(u64_t x) {
    u64_t lo16  = x & 0xFFFFULL;
    u64_t mid32 = (x >> 16) & 0xFFFFFFFFULL;
    u64_t hi16  = x >> 48;
    u64_t t0 = gold_sub(lo16 << 48, hi16);
    u64_t t1 = (mid32 << 32) - mid32;
    return gold_add(t0, t1);
}

__device__ __forceinline__ u64_t gold_div2(u64_t a) {
    return (a >> 1) + ((a & 1ULL) ? GOLD_HALF : 0ULL);
}

__device__ void ntt_dif_smem(u64_t* sbuf, const u64_t* __restrict__ dif_tw, int N, int lgN) {
    int tw_base = 0;
    for (int m = N; m >= 4; m >>= 2) {
        const int q = m >> 2;
        const int n_bfly = N >> 2;
        for (int idx = threadIdx.x; idx < n_bfly; idx += blockDim.x) {
            const int j = idx & (q - 1);
            const int base = (idx ^ j) << 2;
            const u64_t a0 = sbuf[base + j];
            const u64_t a1 = sbuf[base + j + q];
            const u64_t a2 = sbuf[base + j + 2 * q];
            const u64_t a3 = sbuf[base + j + 3 * q];
            const u64_t t0 = gold_add(a0, a2);
            const u64_t t1 = gold_add(a1, a3);
            const u64_t t2 = gold_sub(a0, a2);
            const u64_t t3 = gold_mul_2pow48(gold_sub(a1, a3));
            const u64_t y0 = gold_add(t0, t1);
            u64_t y1 = gold_add(t2, t3);
            u64_t y2 = gold_sub(t0, t1);
            u64_t y3 = gold_sub(t2, t3);
            if (j != 0) {
                const int toff = (tw_base + j) * 3;
                y1 = gold_mul(y1, __ldg(&dif_tw[toff + 0]));
                y2 = gold_mul(y2, __ldg(&dif_tw[toff + 1]));
                y3 = gold_mul(y3, __ldg(&dif_tw[toff + 2]));
            }
            sbuf[base + j]         = y0;
            sbuf[base + j + q]     = y1;
            sbuf[base + j + 2 * q] = y2;
            sbuf[base + j + 3 * q] = y3;
        }
        tw_base += q;
        __syncthreads();
    }
    if (lgN & 1) {
        const int half_N = N >> 1;
        for (int idx = threadIdx.x; idx < half_N; idx += blockDim.x) {
            const int base = idx << 1;
            const u64_t a0 = sbuf[base];
            const u64_t a1 = sbuf[base + 1];
            sbuf[base]     = gold_add(a0, a1);
            sbuf[base + 1] = gold_sub(a0, a1);
        }
        __syncthreads();
    }
}

__device__ void intt_dit_smem(u64_t* sbuf, const u64_t* __restrict__ dit_tw, int N, int lgN) {
    if (lgN & 1) {
        const int half_N = N >> 1;
        for (int idx = threadIdx.x; idx < half_N; idx += blockDim.x) {
            const int base = idx << 1;
            const u64_t a0 = sbuf[base];
            const u64_t a1 = sbuf[base + 1];
            sbuf[base]     = gold_add(a0, a1);
            sbuf[base + 1] = gold_sub(a0, a1);
        }
        __syncthreads();
    }
    int tw_base = 0;
    for (int m = (lgN & 1) ? 8 : 4; m <= N; m <<= 2) {
        const int q = m >> 2;
        const int n_bfly = N >> 2;
        for (int idx = threadIdx.x; idx < n_bfly; idx += blockDim.x) {
            const int j = idx & (q - 1);
            const int base = (idx ^ j) << 2;
            const u64_t z0 = sbuf[base + j];
            u64_t z1 = sbuf[base + j + q];
            u64_t z2 = sbuf[base + j + 2 * q];
            u64_t z3 = sbuf[base + j + 3 * q];
            if (j != 0) {
                const int toff = (tw_base + j) * 3;
                z1 = gold_mul(z1, __ldg(&dit_tw[toff + 0]));
                z2 = gold_mul(z2, __ldg(&dit_tw[toff + 1]));
                z3 = gold_mul(z3, __ldg(&dit_tw[toff + 2]));
            }
            const u64_t u0 = gold_add(z0, z2);
            const u64_t u1 = gold_add(z1, z3);
            const u64_t u2 = gold_sub(z0, z2);
            const u64_t u3 = gold_mul_2pow48(gold_sub(z3, z1));
            sbuf[base + j]         = gold_add(u0, u1);
            sbuf[base + j + q]     = gold_add(u2, u3);
            sbuf[base + j + 2 * q] = gold_sub(u0, u1);
            sbuf[base + j + 3 * q] = gold_sub(u2, u3);
        }
        tw_base += q;
        __syncthreads();
    }
}

__device__ void linear_carry_smem(u64_t* sbuf, unsigned char* G, unsigned char* Pp, int len, int W) {
    const u64_t mask_w = (1ULL << W) - 1ULL;
    const int T = blockDim.x;
    const int tid = threadIdx.x;

    // Backward tile gather (100% race-free in-place)
    for (int base = ((len - 1) / T) * T; base >= 0; base -= T) {
        const int k = base + tid;
        u64_t v = 0ULL;
        if (k < len) {
            v = sbuf[k] & mask_w;
            if (k >= 1) v += (sbuf[k - 1] >> W) & mask_w;
            if (k >= 2) v += (sbuf[k - 2] >> (2 * W)) & mask_w;
            if (3 * W < 64 && k >= 3) v += sbuf[k - 3] >> (3 * W);
        }
        __syncthreads();
        if (k < len) sbuf[k] = v;
        __syncthreads();
    }

    for (int rnd = 0; rnd < 3; ++rnd) {
        for (int base = ((len - 1) / T) * T; base >= 0; base -= T) {
            const int k = base + tid;
            u64_t v = 0ULL;
            if (k < len) {
                v = sbuf[k] & mask_w;
                if (k >= 1) v += sbuf[k - 1] >> W;
            }
            __syncthreads();
            if (k < len) sbuf[k] = v;
            __syncthreads();
        }
    }

    // Kogge-Stone prefix carry-lookahead across [0, len)
    const int seg = (len + T - 1) / T;
    const int lo = tid * seg;
    const int hi = (lo + seg < len) ? (lo + seg) : len;
    unsigned char g = 0, p = 1;
    for (int i = lo; i < hi; ++i) {
        const u64_t vi = sbuf[i];
        const unsigned char gi = (vi >= (1ULL << W)) ? 1 : 0;
        const unsigned char pi = (vi == mask_w) ? 1 : 0;
        g = gi | (pi & g);
        p = pi & p;
    }
    G[tid] = g;
    Pp[tid] = p;
    __syncthreads();

    for (int off = 1; off < T; off <<= 1) {
        unsigned char gn = G[tid], pn = Pp[tid];
        if (tid >= off) {
            gn = gn | (pn & G[tid - off]);
            pn = pn & Pp[tid - off];
        }
        __syncthreads();
        G[tid] = gn;
        Pp[tid] = pn;
        __syncthreads();
    }

    u64_t c = (tid > 0) ? (u64_t)G[tid - 1] : 0ULL;
    for (int i = lo; i < hi; ++i) {
        const u64_t v = sbuf[i] + c;
        c = v >> W;
        sbuf[i] = v & mask_w;
    }
    __syncthreads();
}

// Kernel 1: Split cyclic (blockIdx.x==0) and negacyclic (blockIdx.x==1) squaring in SMEM
extern "C" __global__
void goldilocks_sq_split(
    const u32_t* __restrict__ xbuf,
    u64_t* __restrict__ s_plus_out,
    u64_t* __restrict__ s_minus_out,
    const u64_t* __restrict__ dif_tw,
    const u64_t* __restrict__ dit_tw,
    const u64_t* __restrict__ psi_pows,
    const u64_t* __restrict__ inv_psi_n,
    const u8_t*  __restrict__ d_f_steps,
    const int*      __restrict__ d_base_step,
    const int sub_step,
    const int f_is_one,
    const int B,
    const int L,
    const int W,
    const int N_cyc,
    const int lgN,
    const u64_t inv_N
) {
    extern __shared__ u64_t sbuf[];
    const int is_minus = blockIdx.x;
    const int row = blockIdx.y;
    const u32_t* x_row = xbuf + (long long)row * L;
    const u32_t mask_w = (1u << W) - 1u;

    int do_double = 0;
    if (!f_is_one) {
        const int step_idx = d_base_step[0] + sub_step;
        do_double = (d_f_steps[(long long)step_idx * B + row] == 2u) ? 1 : 0;
    }

    for (int i = threadIdx.x; i < N_cyc; i += blockDim.x) {
        u64_t val = 0ULL;
        if (i < L) {
            if (do_double) {
                const u32_t xi = x_row[i];
                const u32_t prev = (i > 0) ? (x_row[i - 1] >> (W - 1)) : 0u;
                val = (u64_t)(((xi << 1) & mask_w) | prev);
            } else {
                val = (u64_t)x_row[i];
            }
            if (is_minus) {
                val = gold_mul(val, __ldg(&psi_pows[i]));
            }
        }
        sbuf[i] = val;
    }
    __syncthreads();

    ntt_dif_smem(sbuf, dif_tw, N_cyc, lgN);

    for (int i = threadIdx.x; i < N_cyc; i += blockDim.x) {
        const u64_t u = sbuf[i];
        sbuf[i] = gold_mul(u, u);
    }
    __syncthreads();

    intt_dit_smem(sbuf, dit_tw, N_cyc, lgN);

    if (!is_minus) {
        u64_t* dst = s_plus_out + (long long)row * N_cyc;
        for (int i = threadIdx.x; i < N_cyc; i += blockDim.x) {
            dst[i] = gold_mul(sbuf[i], inv_N);
        }
    } else {
        u64_t* dst = s_minus_out + (long long)row * N_cyc;
        for (int i = threadIdx.x; i < N_cyc; i += blockDim.x) {
            dst[i] = gold_mul(sbuf[i], __ldg(&inv_psi_n[i]));
        }
    }
}

// Kernel 2: Fused Proth 2/3-quotient + 1/2-cyclic Montgomery + Cyclic Kogge-Stone in SMEM
extern "C" __global__
void goldilocks_proth_reduce(
    const u64_t* __restrict__ s_plus_in,
    const u64_t* __restrict__ s_minus_in,
    const u64_t* __restrict__ FKinv_ntt,
    const u64_t* __restrict__ FPsh_ntt,
    const u64_t* __restrict__ dif_tw,
    const u64_t* __restrict__ dit_tw,
    u32_t*       __restrict__ tlo_scratch,
    u32_t*       __restrict__ xbuf,
    int*            __restrict__ overflow,
    const int L,
    const int L0,
    const int L1,
    const int W,
    const int N_cyc,
    const int lgN
) {
    extern __shared__ u64_t dyn_smem[];
    u64_t* sbuf = dyn_smem;                                         // N_cyc * 8 B
    u8_t*  hi_byte = (u8_t*)(sbuf + N_cyc);                      // N_cyc * 1 B
    unsigned char* G  = (unsigned char*)(hi_byte + N_cyc);             // 1024 B
    unsigned char* Pp = G + 1024;                                      // 1024 B
    u64_t* wrap_lo = (u64_t*)(Pp + 1024);                        // 2 * 8 B
    u8_t*  wrap_hi = (u8_t*)(wrap_lo + 2);                       // 2 B

    const int row = blockIdx.x;
    const int T = blockDim.x;
    const int tid = threadIdx.x;
    const u64_t mask_w = (1ULL << W) - 1ULL;

    const u64_t* sp_row   = s_plus_in  + (long long)row * N_cyc;
    const u64_t* sm_row   = s_minus_in + (long long)row * N_cyc;
    const u64_t* fkinv_r  = FKinv_ntt  + (long long)row * N_cyc;
    const u64_t* fpsh_r   = FPsh_ntt   + (long long)row * N_cyc;
    u32_t*       tlo_row  = tlo_scratch + (long long)row * L;
    u32_t*       x_row    = xbuf       + (long long)row * L;

    // Step 3: T_lo_raw[0..L-1] = (sp + sm) / 2 -> Linear Kogge-Stone -> save tlo_u32 & pad L1..N_cyc-1
    for (int i = tid; i < L; i += T) {
        sbuf[i] = gold_div2(gold_add(sp_row[i], sm_row[i]));
    }
    __syncthreads();

    linear_carry_smem(sbuf, G, Pp, L, W);

    for (int i = tid; i < N_cyc; i += T) {
        if (i < L) {
            const u32_t v = (u32_t)sbuf[i];
            tlo_row[i] = v;
            if (i >= L1) sbuf[i] = 0ULL;
        } else {
            sbuf[i] = 0ULL;
        }
    }
    __syncthreads();

    // Step 4: m1 = (T_lo[0..L1-1] * K_inv) mod B_limb^L1 (FKinv_ntt is pre-scaled by inv_N!)
    ntt_dif_smem(sbuf, dif_tw, N_cyc, lgN);
    for (int i = tid; i < N_cyc; i += T) {
        sbuf[i] = gold_mul(sbuf[i], __ldg(&fkinv_r[i]));
    }
    __syncthreads();
    intt_dit_smem(sbuf, dit_tw, N_cyc, lgN);

    linear_carry_smem(sbuf, G, Pp, L1, W);

    // Build q_raw[0..L-1] = (MASK - T_lo[i]) + (i==0) + (i>=L0 ? m1[i-L0] : 0) backward-safe
    for (int base = ((L - 1) / T) * T; base >= 0; base -= T) {
        const int i = base + tid;
        u64_t qv = 0ULL;
        if (i < L) {
            qv = (mask_w - (u64_t)tlo_row[i]) + ((i == 0) ? 1ULL : 0ULL);
            if (i >= L0) qv += sbuf[i - L0];
        }
        __syncthreads();
        if (i < L) sbuf[i] = qv;
        __syncthreads();
    }
    for (int i = L + tid; i < N_cyc; i += T) {
        sbuf[i] = 0ULL;
    }
    __syncthreads();

    linear_carry_smem(sbuf, G, Pp, L, W);

    // Step 5: q * P_sh mod (z^N_cyc - 1) (FPsh_ntt is pre-shifted by +L and pre-scaled by inv_N!)
    ntt_dif_smem(sbuf, dif_tw, N_cyc, lgN);
    for (int i = tid; i < N_cyc; i += T) {
        sbuf[i] = gold_mul(sbuf[i], __ldg(&fpsh_r[i]));
    }
    __syncthreads();
    intt_dit_smem(sbuf, dit_tw, N_cyc, lgN);

    // Step 6: Exact 96-bit C'[k] = T_lo_raw[(L+k)%N] + T_hi_raw[(L+k)%N] + qp_sh[k]
    const int n_mask = N_cyc - 1;
    for (int k = tid; k < N_cyc; k += T) {
        const int idx = (L + k) & n_mask;
        const u64_t sp = sp_row[idx];
        const u64_t sm = sm_row[idx];
        const u64_t t0 = gold_div2(gold_add(sp, sm));
        const u64_t t1 = gold_div2(gold_sub(sp, sm));
        const u64_t qp = sbuf[k];

        u64_t lo = t0 + t1;
        u32_t hi = (lo < t0) ? 1u : 0u;
        u64_t lo2 = lo + qp;
        if (lo2 < lo) hi += 1u;
        sbuf[k] = lo2;
        hi_byte[k] = (u8_t)hi;
    }
    __syncthreads();

    // Cyclic Carry Round 1 (96-bit -> < 2^27) using backward tile order + saved wraparound
    if (tid < 2) {
        wrap_lo[tid] = sbuf[N_cyc - 2 + tid];
        wrap_hi[tid] = hi_byte[N_cyc - 2 + tid];
    }
    __syncthreads();

    for (int base = ((N_cyc - 1) / T) * T; base >= 0; base -= T) {
        const int k = base + tid;
        u64_t v = 0ULL;
        if (k < N_cyc) {
            const u64_t cur_lo = sbuf[k];
            u64_t m1_lo, m2_lo;
            u8_t  m1_hi, m2_hi;
            if (k >= 1) { m1_lo = sbuf[k - 1]; m1_hi = hi_byte[k - 1]; }
            else        { m1_lo = wrap_lo[1];  m1_hi = wrap_hi[1];     }
            if (k >= 2) { m2_lo = sbuf[k - 2]; m2_hi = hi_byte[k - 2]; }
            else if (k == 1) { m2_lo = wrap_lo[1]; m2_hi = wrap_hi[1]; }
            else        { m2_lo = wrap_lo[0];  m2_hi = wrap_hi[0];     }

            const u64_t v0 = cur_lo & mask_w;
            const u64_t c1 = ((m1_lo >> W) | ((u64_t)m1_hi << (64 - W))) & mask_w;
            u64_t c2 = 0ULL;
            if (2 * W < 64) {
                c2 = (m2_lo >> (2 * W)) | ((u64_t)m2_hi << (64 - 2 * W));
            } else {
                c2 = (u64_t)m2_hi >> (2 * W - 64);
            }
            v = v0 + c1 + c2;
        }
        __syncthreads();
        if (k < N_cyc) sbuf[k] = v;
        __syncthreads();
    }

    // Cyclic Carry Rounds 2..4 -> every sbuf[k] in [0, 1 << W]
    for (int rnd = 0; rnd < 3; ++rnd) {
        if (tid == 0) wrap_lo[0] = sbuf[N_cyc - 1];
        __syncthreads();
        for (int base = ((N_cyc - 1) / T) * T; base >= 0; base -= T) {
            const int k = base + tid;
            u64_t v = 0ULL;
            if (k < N_cyc) {
                const u64_t prev = (k >= 1) ? sbuf[k - 1] : wrap_lo[0];
                v = (sbuf[k] & mask_w) + (prev >> W);
            }
            __syncthreads();
            if (k < N_cyc) sbuf[k] = v;
            __syncthreads();
        }
    }

    // Single-Pass Cyclic Kogge-Stone End-Around Carry
    const int seg = (N_cyc + T - 1) / T;
    const int lo = tid * seg;
    const int hi = (lo + seg < N_cyc) ? (lo + seg) : N_cyc;
    unsigned char g = 0, p = 1;
    for (int i = lo; i < hi; ++i) {
        const u64_t vi = sbuf[i];
        const unsigned char gi = (vi >= (1ULL << W)) ? 1 : 0;
        const unsigned char pi = (vi == mask_w) ? 1 : 0;
        g = gi | (pi & g);
        p = pi & p;
    }
    G[tid] = g;
    Pp[tid] = p;
    __syncthreads();

    for (int off = 1; off < T; off <<= 1) {
        unsigned char gn = G[tid], pn = Pp[tid];
        if (tid >= off) {
            gn = gn | (pn & G[tid - off]);
            pn = pn & Pp[tid - off];
        }
        __syncthreads();
        G[tid] = gn;
        Pp[tid] = pn;
        __syncthreads();
    }

    const unsigned char c_wrap = G[T - 1];
    const unsigned char all_mask = Pp[T - 1];
    if (all_mask && !c_wrap) {
        for (int i = lo; i < hi; ++i) {
            if (i < L) x_row[i] = 0u;
        }
    } else {
        u64_t c = (tid == 0) ? (u64_t)c_wrap : (u64_t)(G[tid - 1] | (Pp[tid - 1] & c_wrap));
        for (int i = lo; i < hi; ++i) {
            const u64_t v = sbuf[i] + c;
            c = v >> W;
            const u32_t zn = (u32_t)(v & mask_w);
            if (i < L) {
                x_row[i] = zn;
            } else if (zn != 0u) {
                atomicOr(overflow, 4);
            }
        }
    }
}

extern "C" __global__
void inc_base_step(int* d_base_step, const int delta) {
    if (threadIdx.x == 0 && blockIdx.x == 0) {
        d_base_step[0] += delta;
    }
}

extern "C" __global__
void precompute_ntt_prescaled(
    u64_t* __restrict__ data,
    const u64_t* __restrict__ dif_tw,
    const int N_cyc,
    const int lgN,
    const u64_t inv_N
) {
    extern __shared__ u64_t sbuf[];
    const int row = blockIdx.x;
    u64_t* d_row = data + (long long)row * N_cyc;
    for (int i = threadIdx.x; i < N_cyc; i += blockDim.x) sbuf[i] = d_row[i];
    __syncthreads();
    ntt_dif_smem(sbuf, dif_tw, N_cyc, lgN);
    for (int i = threadIdx.x; i < N_cyc; i += blockDim.x) d_row[i] = gold_mul(sbuf[i], inv_N);
}

// --- Two-stage (<= 66.6 KB SMEM) Goldilocks kernels for GPUs with < 148 KB opt-in SMEM (e.g. L4 sm_89) ---
__device__ void linear_carry_u32_smem(u32_t* s32, unsigned char* G, unsigned char* Pp, int len, int W) {
    const u32_t mask_w = (1u << W) - 1u;
    const int T = blockDim.x;
    const int tid = threadIdx.x;
    for (int rnd = 0; rnd < 3; ++rnd) {
        for (int base = ((len - 1) / T) * T; base >= 0; base -= T) {
            const int k = base + tid;
            u32_t v = 0u;
            if (k < len) {
                v = s32[k] & mask_w;
                if (k >= 1) v += s32[k - 1] >> W;
            }
            __syncthreads();
            if (k < len) s32[k] = v;
            __syncthreads();
        }
    }
    const int seg = (len + T - 1) / T;
    const int lo = tid * seg;
    const int hi = (lo + seg < len) ? (lo + seg) : len;
    unsigned char g = 0, p = 1;
    for (int i = lo; i < hi; ++i) {
        const u32_t vi = s32[i];
        const unsigned char gi = (vi >= (1u << W)) ? 1 : 0;
        const unsigned char pi = (vi == mask_w) ? 1 : 0;
        g = gi | (pi & g);
        p = pi & p;
    }
    G[tid] = g; Pp[tid] = p;
    __syncthreads();
    for (int off = 1; off < T; off <<= 1) {
        unsigned char gn = G[tid], pn = Pp[tid];
        if (tid >= off) {
            gn = gn | (pn & G[tid - off]);
            pn = pn & Pp[tid - off];
        }
        __syncthreads();
        G[tid] = gn; Pp[tid] = pn;
        __syncthreads();
    }
    u32_t c = (tid > 0) ? (u32_t)G[tid - 1] : 0u;
    for (int i = lo; i < hi; ++i) {
        const u32_t v = s32[i] + c;
        c = v >> W;
        s32[i] = v & mask_w;
    }
    __syncthreads();
}

extern "C" __global__
void gold_2s_prep_sq(
    const u32_t* __restrict__ xbuf,
    u64_t* __restrict__ s_plus,
    u64_t* __restrict__ s_minus,
    const u64_t* __restrict__ psi_pows,
    const u8_t*  __restrict__ d_f_steps,
    const int*   __restrict__ d_base_step,
    const int sub_step, const int f_is_one,
    const int B, const int L, const int W, const int N_cyc
) {
    const int row = blockIdx.y;
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N_cyc) return;
    u64_t vp = 0ULL, vm = 0ULL;
    if (i < L) {
        const u32_t* xr = xbuf + (long long)row * L;
        const u32_t mask_w = (1u << W) - 1u;
        int do_double = 0;
        if (!f_is_one) {
            const int step_idx = d_base_step[0] + sub_step;
            do_double = (d_f_steps[(long long)step_idx * B + row] == 2u) ? 1 : 0;
        }
        if (do_double) {
            const u32_t xi = xr[i];
            const u32_t prev = (i > 0) ? (xr[i - 1] >> (W - 1)) : 0u;
            vp = (u64_t)(((xi << 1) & mask_w) | prev);
        } else {
            vp = (u64_t)xr[i];
        }
        vm = gold_mul(vp, __ldg(&psi_pows[i]));
    }
    s_plus[(long long)row * N_cyc + i]  = vp;
    s_minus[(long long)row * N_cyc + i] = vm;
}

extern "C" __global__
void gold_2s_outer_dif(u64_t* __restrict__ data, const u64_t* __restrict__ dif_tw, const int N_cyc) {
    const int Q = N_cyc >> 2;
    const int j = blockIdx.x * blockDim.x + threadIdx.x;
    if (j >= Q) return;
    u64_t* d = data + (long long)blockIdx.y * N_cyc;
    const u64_t a0 = d[j], a1 = d[j + Q], a2 = d[j + 2 * Q], a3 = d[j + 3 * Q];
    const u64_t t0 = gold_add(a0, a2), t1 = gold_add(a1, a3);
    const u64_t t2 = gold_sub(a0, a2), t3 = gold_mul_2pow48(gold_sub(a1, a3));
    u64_t y0 = gold_add(t0, t1), y1 = gold_add(t2, t3), y2 = gold_sub(t0, t1), y3 = gold_sub(t2, t3);
    if (j != 0) {
        const int toff = j * 3;
        y1 = gold_mul(y1, __ldg(&dif_tw[toff + 0]));
        y2 = gold_mul(y2, __ldg(&dif_tw[toff + 1]));
        y3 = gold_mul(y3, __ldg(&dif_tw[toff + 2]));
    }
    d[j] = y0; d[j + Q] = y1; d[j + 2 * Q] = y2; d[j + 3 * Q] = y3;
}

extern "C" __global__
void gold_2s_sub_dif_scale(
    u64_t* __restrict__ data, const u64_t* __restrict__ dif_tw,
    const int N_cyc, const int lgN, const u64_t inv_N
) {
    extern __shared__ u64_t sbuf[];
    const int Q = N_cyc >> 2;
    const int q_idx = blockIdx.x;
    const int row = blockIdx.y;
    u64_t* d = data + (long long)row * N_cyc + (long long)q_idx * Q;
    for (int i = threadIdx.x; i < Q; i += blockDim.x) sbuf[i] = d[i];
    __syncthreads();
    ntt_dif_smem(sbuf, dif_tw + 3 * Q, Q, lgN - 2);
    for (int i = threadIdx.x; i < Q; i += blockDim.x) d[i] = gold_mul(sbuf[i], inv_N);
}

extern "C" __global__
void gold_2s_sub_sq_or_mul(
    u64_t* __restrict__ data,
    const u64_t* __restrict__ factor,
    const int is_sq,
    const u64_t* __restrict__ dif_tw,
    const u64_t* __restrict__ dit_tw,
    const int N_cyc,
    const int lgN
) {
    extern __shared__ u64_t sbuf[];
    const int Q = N_cyc >> 2;
    const int lgQ = lgN - 2;
    const int q_idx = blockIdx.x;
    const int row = blockIdx.y;
    const long long off = (long long)row * N_cyc + (long long)q_idx * Q;
    u64_t* d = data + off;
    for (int i = threadIdx.x; i < Q; i += blockDim.x) sbuf[i] = d[i];
    __syncthreads();
    ntt_dif_smem(sbuf, dif_tw + 3 * Q, Q, lgQ);
    if (is_sq) {
        for (int i = threadIdx.x; i < Q; i += blockDim.x) {
            const u64_t u = sbuf[i];
            sbuf[i] = gold_mul(u, u);
        }
    } else {
        const u64_t* f_sub = factor + off;
        for (int i = threadIdx.x; i < Q; i += blockDim.x) {
            sbuf[i] = gold_mul(sbuf[i], __ldg(&f_sub[i]));
        }
    }
    __syncthreads();
    intt_dit_smem(sbuf, dit_tw, Q, lgQ);
    for (int i = threadIdx.x; i < Q; i += blockDim.x) d[i] = sbuf[i];
}

extern "C" __global__
void gold_2s_outer_dit(
    u64_t* __restrict__ data,
    const u64_t* __restrict__ dit_tw,
    const int dit_outer_off,
    const u64_t* __restrict__ inv_psi_n,
    const u64_t inv_N,
    const int scale_mode,
    const int N_cyc
) {
    const int Q = N_cyc >> 2;
    const int j = blockIdx.x * blockDim.x + threadIdx.x;
    if (j >= Q) return;
    u64_t* d = data + (long long)blockIdx.y * N_cyc;
    const u64_t z0 = d[j];
    u64_t z1 = d[j + Q], z2 = d[j + 2 * Q], z3 = d[j + 3 * Q];
    if (j != 0) {
        const int toff = dit_outer_off + j * 3;
        z1 = gold_mul(z1, __ldg(&dit_tw[toff + 0]));
        z2 = gold_mul(z2, __ldg(&dit_tw[toff + 1]));
        z3 = gold_mul(z3, __ldg(&dit_tw[toff + 2]));
    }
    const u64_t u0 = gold_add(z0, z2), u1 = gold_add(z1, z3);
    const u64_t u2 = gold_sub(z0, z2), u3 = gold_mul_2pow48(gold_sub(z3, z1));
    u64_t r0 = gold_add(u0, u1), r1 = gold_add(u2, u3), r2 = gold_sub(u0, u1), r3 = gold_sub(u2, u3);
    if (scale_mode == 1) {
        r0 = gold_mul(r0, inv_N); r1 = gold_mul(r1, inv_N);
        r2 = gold_mul(r2, inv_N); r3 = gold_mul(r3, inv_N);
    } else if (scale_mode == 2) {
        r0 = gold_mul(r0, __ldg(&inv_psi_n[j]));
        r1 = gold_mul(r1, __ldg(&inv_psi_n[j + Q]));
        r2 = gold_mul(r2, __ldg(&inv_psi_n[j + 2 * Q]));
        r3 = gold_mul(r3, __ldg(&inv_psi_n[j + 3 * Q]));
    }
    d[j] = r0; d[j + Q] = r1; d[j + 2 * Q] = r2; d[j + 3 * Q] = r3;
}

extern "C" __global__
void gold_2s_tlo_norm(
    const u64_t* __restrict__ s_plus,
    const u64_t* __restrict__ s_minus,
    u32_t* __restrict__ tlo_scratch,
    u64_t* __restrict__ d_work,
    const int L, const int L1, const int W, const int N_cyc
) {
    extern __shared__ u32_t smem32[];
    u32_t* s32 = smem32;
    unsigned char* G = (unsigned char*)(s32 + L);
    unsigned char* Pp = G + 1024;
    const int row = blockIdx.x;
    const int tid = threadIdx.x, T = blockDim.x;
    const u64_t mask_w = (1ULL << W) - 1ULL;
    const u64_t* sp = s_plus  + (long long)row * N_cyc;
    const u64_t* sm = s_minus + (long long)row * N_cyc;

    for (int k = tid; k < L; k += T) {
        const u64_t c0 = gold_div2(gold_add(sp[k], sm[k]));
        u64_t v = c0 & mask_w;
        if (k >= 1) {
            const u64_t c1 = gold_div2(gold_add(sp[k - 1], sm[k - 1]));
            v += (c1 >> W) & mask_w;
        }
        if (k >= 2) {
            const u64_t c2 = gold_div2(gold_add(sp[k - 2], sm[k - 2]));
            v += (c2 >> (2 * W)) & mask_w;
        }
        if (3 * W < 64 && k >= 3) {
            const u64_t c3 = gold_div2(gold_add(sp[k - 3], sm[k - 3]));
            v += c3 >> (3 * W);
        }
        s32[k] = (u32_t)v;
    }
    __syncthreads();
    linear_carry_u32_smem(s32, G, Pp, L, W);

    u32_t* tlo_r = tlo_scratch + (long long)row * L;
    u64_t* wk_r  = d_work + (long long)row * N_cyc;
    for (int i = tid; i < N_cyc; i += T) {
        if (i < L) {
            const u32_t v = s32[i];
            tlo_r[i] = v;
            wk_r[i] = (i < L1) ? (u64_t)v : 0ULL;
        } else {
            wk_r[i] = 0ULL;
        }
    }
}

extern "C" __global__
void gold_2s_m1_q_norm(
    u64_t* __restrict__ d_work,
    const u32_t* __restrict__ tlo_scratch,
    const int L, const int L0, const int L1, const int W, const int N_cyc
) {
    extern __shared__ u32_t smem32[];
    u32_t* s32 = smem32;
    unsigned char* G = (unsigned char*)(s32 + L);
    unsigned char* Pp = G + 1024;
    const int row = blockIdx.x;
    const int tid = threadIdx.x, T = blockDim.x;
    const u64_t mask_w = (1ULL << W) - 1ULL;
    u64_t* wk_r = d_work + (long long)row * N_cyc;
    const u32_t* tlo_r = tlo_scratch + (long long)row * L;

    for (int k = tid; k < L1; k += T) {
        u64_t v = wk_r[k] & mask_w;
        if (k >= 1) v += (wk_r[k - 1] >> W) & mask_w;
        if (k >= 2) v += (wk_r[k - 2] >> (2 * W)) & mask_w;
        if (3 * W < 64 && k >= 3) v += wk_r[k - 3] >> (3 * W);
        s32[k] = (u32_t)v;
    }
    __syncthreads();
    linear_carry_u32_smem(s32, G, Pp, L1, W);

    const u32_t mask32 = (1u << W) - 1u;
    for (int base = ((L - 1) / T) * T; base >= 0; base -= T) {
        const int i = base + tid;
        u32_t qv = 0u;
        if (i < L) {
            qv = (mask32 - tlo_r[i]) + ((i == 0) ? 1u : 0u);
            if (i >= L0) qv += s32[i - L0];
        }
        __syncthreads();
        if (i < L) s32[i] = qv;
        __syncthreads();
    }
    linear_carry_u32_smem(s32, G, Pp, L, W);

    for (int i = tid; i < N_cyc; i += T) {
        wk_r[i] = (i < L) ? (u64_t)s32[i] : 0ULL;
    }
}

__device__ __forceinline__ void eval_c96_gmem(
    const u64_t* __restrict__ sp_r,
    const u64_t* __restrict__ sm_r,
    const u64_t* __restrict__ qp_r,
    const int k, const int L, const int n_mask,
    u64_t& out_lo, u32_t& out_hi
) {
    const int idx = (L + k) & n_mask;
    const u64_t sp = sp_r[idx];
    const u64_t sm = sm_r[idx];
    const u64_t t0 = gold_div2(gold_add(sp, sm));
    const u64_t t1 = gold_div2(gold_sub(sp, sm));
    const u64_t qp = qp_r[k];
    u64_t lo = t0 + t1;
    u32_t hi = (lo < t0) ? 1u : 0u;
    u64_t lo2 = lo + qp;
    if (lo2 < lo) hi += 1u;
    out_lo = lo2;
    out_hi = hi;
}

extern "C" __global__
void gold_2s_cyclic_reduce(
    const u64_t* __restrict__ s_plus,
    const u64_t* __restrict__ s_minus,
    const u64_t* __restrict__ qp_sh,
    u32_t* __restrict__ xbuf,
    int* __restrict__ overflow,
    const int L, const int W, const int N_cyc
) {
    extern __shared__ u32_t smem32[];
    u32_t* s32 = smem32;
    unsigned char* G = (unsigned char*)(s32 + N_cyc);
    unsigned char* Pp = G + 1024;
    u32_t* wrap32 = (u32_t*)(Pp + 1024);

    const int row = blockIdx.x;
    const int tid = threadIdx.x, T = blockDim.x;
    const u64_t mask_w = (1ULL << W) - 1ULL;
    const u32_t mask32 = (1u << W) - 1u;
    const int n_mask = N_cyc - 1;

    const u64_t* sp_r = s_plus  + (long long)row * N_cyc;
    const u64_t* sm_r = s_minus + (long long)row * N_cyc;
    const u64_t* qp_r = qp_sh   + (long long)row * N_cyc;
    u32_t* xr = xbuf + (long long)row * L;

    for (int k = tid; k < N_cyc; k += T) {
        u64_t c0_lo, c1_lo, c2_lo;
        u32_t c0_hi, c1_hi, c2_hi;
        eval_c96_gmem(sp_r, sm_r, qp_r, k, L, n_mask, c0_lo, c0_hi);
        eval_c96_gmem(sp_r, sm_r, qp_r, (k - 1) & n_mask, L, n_mask, c1_lo, c1_hi);
        eval_c96_gmem(sp_r, sm_r, qp_r, (k - 2) & n_mask, L, n_mask, c2_lo, c2_hi);
        const u64_t v0 = c0_lo & mask_w;
        const u64_t c1 = ((c1_lo >> W) | ((u64_t)c1_hi << (64 - W))) & mask_w;
        u64_t c2 = 0ULL;
        if (2 * W < 64) c2 = (c2_lo >> (2 * W)) | ((u64_t)c2_hi << (64 - 2 * W));
        else            c2 = (u64_t)c2_hi >> (2 * W - 64);
        s32[k] = (u32_t)(v0 + c1 + c2);
    }
    __syncthreads();

    for (int rnd = 0; rnd < 3; ++rnd) {
        if (tid == 0) wrap32[0] = s32[N_cyc - 1];
        __syncthreads();
        for (int base = ((N_cyc - 1) / T) * T; base >= 0; base -= T) {
            const int k = base + tid;
            u32_t v = 0u;
            if (k < N_cyc) {
                const u32_t prev = (k >= 1) ? s32[k - 1] : wrap32[0];
                v = (s32[k] & mask32) + (prev >> W);
            }
            __syncthreads();
            if (k < N_cyc) s32[k] = v;
            __syncthreads();
        }
    }

    const int seg = (N_cyc + T - 1) / T;
    const int lo = tid * seg;
    const int hi = (lo + seg < N_cyc) ? (lo + seg) : N_cyc;
    unsigned char g = 0, p = 1;
    for (int i = lo; i < hi; ++i) {
        const u32_t vi = s32[i];
        const unsigned char gi = (vi >= (1u << W)) ? 1 : 0;
        const unsigned char pi = (vi == mask32) ? 1 : 0;
        g = gi | (pi & g);
        p = pi & p;
    }
    G[tid] = g; Pp[tid] = p;
    __syncthreads();

    for (int off = 1; off < T; off <<= 1) {
        unsigned char gn = G[tid], pn = Pp[tid];
        if (tid >= off) {
            gn = gn | (pn & G[tid - off]);
            pn = pn & Pp[tid - off];
        }
        __syncthreads();
        G[tid] = gn; Pp[tid] = pn;
        __syncthreads();
    }

    const unsigned char c_wrap = G[T - 1];
    const unsigned char all_mask = Pp[T - 1];
    if (all_mask && !c_wrap) {
        for (int i = lo; i < hi; ++i) {
            if (i < L) xr[i] = 0u;
        }
    } else {
        u32_t c = (tid == 0) ? (u32_t)c_wrap : (u32_t)(G[tid - 1] | (Pp[tid - 1] & c_wrap));
        for (int i = lo; i < hi; ++i) {
            const u32_t v = s32[i] + c;
            c = v >> W;
            const u32_t zn = v & mask32;
            if (i < L) xr[i] = zn;
            else if (zn != 0u) atomicOr(overflow, 4);
        }
    }
}
"""

_CUFFT_PROTH_CUDA_SRC = r"""
using u8_t = unsigned char;

extern "C" __global__
void prep_y15(
    const double* __restrict__ xbuf, const long long x_stride,
    double* __restrict__ ybuf, const long long y_stride,
    const u8_t* __restrict__ d_f_steps, const int* __restrict__ d_base_step,
    const int sub_step, const int f_is_one, const int B, const int L
) {
    const int row = blockIdx.y;
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= L) return;
    const double* xr = xbuf + (long long)row * x_stride;
    double* yr = ybuf + (long long)row * y_stride;
    int do_double = 0;
    if (!f_is_one) {
        const int step_idx = d_base_step[0] + sub_step;
        do_double = (d_f_steps[(long long)step_idx * B + row] == 2u) ? 1 : 0;
    }
    if (do_double) {
        const int xi = (int)xr[i];
        const int prev = (i > 0) ? (((int)xr[i - 1]) >> 14) : 0;
        yr[i] = (double)(((xi << 1) & 0x7FFF) | prev);
    } else {
        yr[i] = xr[i];
    }
}

extern "C" __global__
void cufft_sq_scale(double2* __restrict__ X, const int n_freq, const double inv_N) {
    const int row = blockIdx.y;
    const int col = blockIdx.x * blockDim.x + threadIdx.x;
    if (col >= n_freq) return;
    double2* p = X + (long long)row * n_freq + col;
    const double re = p->x, im = p->y;
    p->x = (re * re - im * im) * inv_N;
    p->y = (2.0 * re * im) * inv_N;
}

extern "C" __global__
void cufft_cmul_inplace(
    double2* __restrict__ A,
    const double2* __restrict__ B_pre,
    const int n_freq
) {
    const int row = blockIdx.y;
    const int col = blockIdx.x * blockDim.x + threadIdx.x;
    if (col >= n_freq) return;
    double2* pa = A + (long long)row * n_freq + col;
    const double2 b = B_pre[(long long)row * n_freq + col];
    const double ar = pa->x, ai = pa->y;
    pa->x = ar * b.x - ai * b.y;
    pa->y = ar * b.y + ai * b.x;
}

extern "C" __global__
void norm15_v4(
    const double* __restrict__ src, const long long src_stride, const int n_src,
    double* __restrict__ dst, const long long dst_stride, const int n_dst,
    unsigned int* __restrict__ maxerr_bits, int* __restrict__ overflow, int* __restrict__ rowflag
) {
    const int H = 8;
    extern __shared__ long long buf[];
    const int W = blockDim.x + H;
    long long* A = buf;
    long long* B = buf + W;
    const long long row = blockIdx.y;
    const int base = blockIdx.x * blockDim.x - H;
    const double* s = src + row * src_stride;
    double* d = dst + row * dst_stride;
    for (int k = threadIdx.x; k < W; k += blockDim.x) {
        const int i = base + k;
        long long v = 0;
        if (i >= 0 && i < n_src) {
            const double x = s[i];
            const double r = rint(x);
            const float e = fabsf((float)(x - r));
            if (e > 0.0f) atomicMax(maxerr_bits, __float_as_uint(e));
            v = (long long)r;
            if (v < 0) { v = 0; atomicOr(overflow, 2); }
        }
        A[k] = v;
    }
    __syncthreads();
    for (int k = threadIdx.x; k < W; k += blockDim.x) {
        long long v = A[k] & 0x7FFF;
        if (k >= 1) v += (A[k - 1] >> 15) & 0x7FFF;
        if (k >= 2) v += (A[k - 2] >> 30) & 0x7FFF;
        if (k >= 3) v += (A[k - 3] >> 45);
        B[k] = v;
    }
    __syncthreads();
    long long* cur = B;
    long long* nxt = A;
    for (int round = 0; round < 4; ++round) {
        for (int k = threadIdx.x; k < W; k += blockDim.x) {
            long long v = cur[k] & 0x7FFF;
            if (k >= 1) v += cur[k - 1] >> 15;
            nxt[k] = v;
        }
        __syncthreads();
        long long* t = cur; cur = nxt; nxt = t;
    }
    for (int k = threadIdx.x + H; k < W; k += blockDim.x) {
        const int i = base + k;
        if (i < n_dst) {
            const long long v = cur[k];
            if (v > 0x8000) atomicOr(overflow, 1);
            if (v == 0x8000) rowflag[row] = 1;
            d[i] = (double)v;
        }
    }
}

extern "C" __global__
void resolve15_v4(double* __restrict__ data, const long long stride, const int n, int* __restrict__ rowflag) {
    __shared__ unsigned char G[1024];
    __shared__ unsigned char Pp[1024];
    const int row = blockIdx.x;
    if (rowflag[row] == 0) return;
    const int tid = threadIdx.x, T = blockDim.x;
    double* d = data + (long long)row * stride;
    const int seg = (n + T - 1) / T;
    const int lo = tid * seg;
    const int hi = min(n, lo + seg);
    unsigned char g = 0, p = 1;
    for (int i = lo; i < hi; ++i) {
        const int v = (int)d[i];
        const unsigned char gi = (v >= 0x8000), pi = (v == 0x7FFF);
        g = gi | (pi & g);
        p = pi & p;
    }
    G[tid] = g; Pp[tid] = p;
    __syncthreads();
    for (int off = 1; off < T; off <<= 1) {
        unsigned char gn = G[tid], pn = Pp[tid];
        if (tid >= off) {
            gn = gn | (pn & G[tid - off]);
            pn = pn & Pp[tid - off];
        }
        __syncthreads();
        G[tid] = gn; Pp[tid] = pn;
        __syncthreads();
    }
    int c = (tid > 0) ? G[tid - 1] : 0;
    for (int i = lo; i < hi; ++i) {
        const int v = (int)d[i] + c;
        c = v >> 15;
        d[i] = (double)(v & 0x7FFF);
    }
    __syncthreads();
    if (tid == 0) rowflag[row] = 0;
}

extern "C" __global__
void copy_tlo_prefix15(
    const double* __restrict__ tlo, const long long tlo_stride,
    double* __restrict__ t1buf, const long long t1_stride, const int L1
) {
    const int row = blockIdx.y;
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= L1) return;
    t1buf[(long long)row * t1_stride + i] = tlo[(long long)row * tlo_stride + i];
}

extern "C" __global__
void build_proth_q15(
    const double* __restrict__ tlo, const long long tlo_stride,
    const double* __restrict__ m1, const long long m1_stride,
    double* __restrict__ qbuf, const long long q_stride,
    const int L, const int L0, int* __restrict__ rowflag
) {
    __shared__ unsigned char G[1024];
    __shared__ unsigned char Pp[1024];
    const int row = blockIdx.x;
    const int tid = threadIdx.x, T = blockDim.x;
    const double* tr = tlo + (long long)row * tlo_stride;
    const double* mr = m1  + (long long)row * m1_stride;
    double* qr = qbuf + (long long)row * q_stride;
    (void)rowflag;

    const int seg = (L + T - 1) / T;
    const int lo = tid * seg;
    const int hi = min(L, lo + seg);

    // Local sequential carry within segment, then Kogge-Stone across segments!
    int c_loc = 0;
    unsigned char p_seg = 1;
    for (int i = lo; i < hi; ++i) {
        int qv = (0x7FFF - (int)tr[i]) + ((i == 0) ? 1 : 0) + ((i >= L0) ? (int)mr[i - L0] : 0) + c_loc;
        c_loc = qv >> 15;
        const int digit = qv & 0x7FFF;
        qr[i] = (double)digit;
        p_seg = p_seg & ((digit == 0x7FFF) ? 1 : 0);
    }
    G[tid] = (unsigned char)c_loc; // note max qv <= 2*0x7FFF + 1 -> c_loc in {0, 1}!
    Pp[tid] = p_seg;
    __syncthreads();

    for (int off = 1; off < T; off <<= 1) {
        unsigned char gn = G[tid], pn = Pp[tid];
        if (tid >= off) {
            gn = gn | (pn & G[tid - off]);
            pn = pn & Pp[tid - off];
        }
        __syncthreads();
        G[tid] = gn; Pp[tid] = pn;
        __syncthreads();
    }

    int c = (tid > 0) ? (int)G[tid - 1] : 0;
    if (c) {
        for (int i = lo; i < hi; ++i) {
            const int v = (int)qr[i] + c;
            c = v >> 15;
            qr[i] = (double)(v & 0x7FFF);
            if (!c) break;
        }
    }
}

__device__ __forceinline__ long long read_c_fold(
    const double* __restrict__ tr,
    const double* __restrict__ qpr,
    const int k,
    const int L,
    const int N_cyc,
    const int max_t_idx,
    unsigned int* __restrict__ maxerr_bits,
    int* __restrict__ overflow
) {
    int j0 = L + k;
    if (j0 >= N_cyc) j0 -= N_cyc;
    const double xqp = qpr[k];
    const double rqp = rint(xqp);
    float emax = fabsf((float)(xqp - rqp));
    long long sum = (long long)rqp;
    if (j0 <= max_t_idx) {
        const double xt0 = tr[j0];
        const double rt0 = rint(xt0);
        float e0 = fabsf((float)(xt0 - rt0));
        if (e0 > emax) emax = e0;
        sum += (long long)rt0;
    }
    const int j1 = j0 + N_cyc;
    if (j1 <= max_t_idx) {
        const double xt1 = tr[j1];
        const double rt1 = rint(xt1);
        float e1 = fabsf((float)(xt1 - rt1));
        if (e1 > emax) emax = e1;
        sum += (long long)rt1;
    }
    if (emax > 0.0f) atomicMax(maxerr_bits, __float_as_uint(emax));
    if (sum < 0) { sum = 0; atomicOr(overflow, 2); }
    return sum;
}

extern "C" __global__
void fold_cyclic_resolve15(
    const double* __restrict__ T_raw, const long long t_stride, const int max_t_idx,
    const double* __restrict__ qp_sh, const long long qp_stride, const int N_cyc,
    double* __restrict__ xbuf, const long long x_stride, const int L,
    unsigned int* __restrict__ maxerr_bits, int* __restrict__ overflow
) {
    extern __shared__ int s_cyc[];
    int* z = s_cyc;
    unsigned char* G  = (unsigned char*)(z + N_cyc);
    unsigned char* Pp = G + 1024;
    long long* wrap_raw = (long long*)(Pp + 1024);

    const int row = blockIdx.x;
    const int T = blockDim.x;
    const int tid = threadIdx.x;
    const double* tr  = T_raw + (long long)row * t_stride;
    const double* qpr = qp_sh + (long long)row * qp_stride;
    double* xr = xbuf + (long long)row * x_stride;

    if (tid < 3) {
        wrap_raw[tid] = read_c_fold(tr, qpr, N_cyc - 3 + tid, L, N_cyc, max_t_idx, maxerr_bits, overflow);
    }
    __syncthreads();

    for (int k = tid; k < N_cyc; k += T) {
        const long long c0 = read_c_fold(tr, qpr, k, L, N_cyc, max_t_idx, maxerr_bits, overflow);
        const long long cm1 = (k >= 1) ? read_c_fold(tr, qpr, k - 1, L, N_cyc, max_t_idx, maxerr_bits, overflow) : wrap_raw[2];
        const long long cm2 = (k >= 2) ? read_c_fold(tr, qpr, k - 2, L, N_cyc, max_t_idx, maxerr_bits, overflow) : ((k == 1) ? wrap_raw[2] : wrap_raw[1]);
        const long long cm3 = (k >= 3) ? read_c_fold(tr, qpr, k - 3, L, N_cyc, max_t_idx, maxerr_bits, overflow) : ((k == 2) ? wrap_raw[2] : ((k == 1) ? wrap_raw[1] : wrap_raw[0]));
        long long v = (c0 & 0x7FFF)
                    + ((cm1 >> 15) & 0x7FFF)
                    + ((cm2 >> 30) & 0x7FFF)
                    + (cm3 >> 45);
        z[k] = (int)v;
    }
    __syncthreads();

    for (int rnd = 0; rnd < 3; ++rnd) {
        if (tid == 0) wrap_raw[0] = (long long)z[N_cyc - 1];
        __syncthreads();
        for (int base = ((N_cyc - 1) / T) * T; base >= 0; base -= T) {
            const int k = base + tid;
            int v = 0;
            if (k < N_cyc) {
                const int prev = (k >= 1) ? z[k - 1] : (int)wrap_raw[0];
                v = (z[k] & 0x7FFF) + (prev >> 15);
            }
            __syncthreads();
            if (k < N_cyc) z[k] = v;
            __syncthreads();
        }
    }

    const int seg = (N_cyc + T - 1) / T;
    const int lo = tid * seg;
    const int hi = min(N_cyc, lo + seg);
    unsigned char g = 0, p = 1;
    for (int i = lo; i < hi; ++i) {
        const int vi = z[i];
        const unsigned char gi = (vi >= 0x8000) ? 1 : 0;
        const unsigned char pi = (vi == 0x7FFF) ? 1 : 0;
        g = gi | (pi & g);
        p = pi & p;
    }
    G[tid] = g; Pp[tid] = p;
    __syncthreads();

    for (int off = 1; off < T; off <<= 1) {
        unsigned char gn = G[tid], pn = Pp[tid];
        if (tid >= off) {
            gn = gn | (pn & G[tid - off]);
            pn = pn & Pp[tid - off];
        }
        __syncthreads();
        G[tid] = gn; Pp[tid] = pn;
        __syncthreads();
    }

    const unsigned char c_wrap = G[T - 1];
    const unsigned char all_mask = Pp[T - 1];
    if (all_mask && !c_wrap) {
        for (int i = lo; i < hi; ++i) {
            if (i < L) xr[i] = 0.0;
        }
    } else {
        int c = (tid == 0) ? (int)c_wrap : (int)(G[tid - 1] | (Pp[tid - 1] & c_wrap));
        for (int i = lo; i < hi; ++i) {
            const int v = z[i] + c;
            c = v >> 15;
            const int zn = v & 0x7FFF;
            if (i < L) xr[i] = (double)zn;
            else if (zn != 0) atomicOr(overflow, 4);
        }
    }
}

extern "C" __global__
void inc_base_step_cufft(int* d_base_step, const int delta) {
    if (threadIdx.x == 0 && blockIdx.x == 0) {
        d_base_step[0] += delta;
    }
}
"""

_GOLD_MOD_CACHE: Any = None
_CUFFT_MOD_CACHE: Any = None


def _get_goldilocks_module(ptxas_verbose: bool = False) -> Any:
    global _GOLD_MOD_CACHE
    if _GOLD_MOD_CACHE is None or ptxas_verbose:
        opts = ("--std=c++17", "-Xptxas=-v") if ptxas_verbose else ("--std=c++17",)
        mod = cp.RawModule(code=_GOLDILOCKS_CUDA_SRC, options=opts)
        mod.compile()
        if not ptxas_verbose:
            _GOLD_MOD_CACHE = mod
        return mod
    return _GOLD_MOD_CACHE


def _get_cufft_module(ptxas_verbose: bool = False) -> Any:
    global _CUFFT_MOD_CACHE
    if _CUFFT_MOD_CACHE is None or ptxas_verbose:
        opts = ("--std=c++17", "-Xptxas=-v") if ptxas_verbose else ("--std=c++17",)
        mod = cp.RawModule(code=_CUFFT_PROTH_CUDA_SRC, options=opts)
        mod.compile()
        if not ptxas_verbose:
            _CUFFT_MOD_CACHE = mod
        return mod
    return _CUFFT_MOD_CACHE


# ---------------------------------------------------------------------------
# BatchScreenV4 (Supports GPU `goldilocks_ntt_graph`, GPU `proth_cufft_graph`, & CPU fallback)
# ---------------------------------------------------------------------------
class BatchScreenV4:
    """Batched 2^((P_j - 1)/2) mod P_j screener for P_j = m_j * 2^n + 1."""

    def __init__(
        self,
        n: int,
        ms: Any,
        gmpy2: Any = None,
        *,
        backend: str = "auto",
        graph_chunk: int = 64,
    ):
        self.g = gmpy2 if gmpy2 is not None else _default_gmpy2
        self.n = int(n)
        self.ms = [int(m) for m in ms]
        self.P = [(m << self.n) + 1 for m in self.ms]
        self.B = len(self.P)
        self.graph_chunk = max(1, int(graph_chunk))

        if backend == "auto":
            self.backend = "goldilocks_ntt_graph" if has_gpu() else "cpu"
        else:
            self.backend = backend

        if self.backend == "cpu" or self.B == 0:
            self._cpu_eng = ProthCPUEngine(self.n, self.ms, engine="proth_ntt") if self.B > 0 else None
            self.L = self._cpu_eng.L if self._cpu_eng else 0
            self.N = self._cpu_eng.N_cyc if self._cpu_eng else 0
            self.K0 = self._cpu_eng.K0 if self._cpu_eng else 0
            return

        if not has_gpu():
            raise RuntimeError(f"GPU backend {self.backend!r} requested, but no CUDA GPU is available")

        self.K0 = max(m.bit_length() for m in self.ms)
        mb = np.zeros((self.B, self.K0), dtype=np.uint8)
        for j, m in enumerate(self.ms):
            s = bin(m)[2:]
            mb[j, self.K0 - len(s) :] = np.frombuffer(s.encode("ascii"), np.uint8) - 48
        # Pre-stage d_f_steps padded to >= graph_chunk + 1 rows so head graph capture never reads OOB
        n_f_rows = max(self.K0 + 1, self.graph_chunk + 1)
        f_steps_host = np.ones((n_f_rows, self.B), dtype=np.uint8)
        if self.K0 > 0:
            f_steps_host[1 : self.K0 + 1, :] = 1 + mb.T
        self.d_f_steps = cp.asarray(np.ascontiguousarray(f_steps_host))
        self.f_steps_host = f_steps_host
        self.d_base_step = cp.zeros(1, dtype=cp.int32)
        self.overflow = cp.zeros(1, dtype=cp.int32)
        self.maxerr = cp.zeros(1, dtype=cp.uint32)
        self.stream = cp.cuda.Stream(non_blocking=True)

        bits = max(p.bit_length() for p in self.P)
        dev_attrs = cp.cuda.Device().attributes
        max_smem_optin = int(dev_attrs.get("MaxSharedMemoryPerBlockOptin", 49152))

        if self.backend in ("goldilocks_ntt_graph", "ntt", "v4_goldilocks_ntt_graph"):
            W, _, L, L0, L1, N_cyc = _choose_goldilocks_params(bits, self.n)
            smem_reduce = N_cyc * 8 + N_cyc + 2048 + 32
            smem_2s_cyc = N_cyc * 4 + 2064
            if smem_reduce <= max_smem_optin:
                self._init_goldilocks_gpu(W, L, L0, L1, N_cyc, two_stage=False, max_smem=max_smem_optin)
                return
            if N_cyc >= 256 and smem_2s_cyc <= max_smem_optin:
                self._init_goldilocks_gpu(W, L, L0, L1, N_cyc, two_stage=True, max_smem=max_smem_optin)
                return
            self.backend = "proth_cufft_graph"

        if self.backend in ("proth_cufft_graph", "cufft_graph", "v4_proth_cufft_graph"):
            self._init_cufft_gpu(bits, max_smem_optin)
        else:
            raise ValueError(f"Unknown BatchScreenV4 backend: {self.backend!r}")

    def _init_goldilocks_gpu(
        self, W: int, L: int, L0: int, L1: int, N_cyc: int, *, two_stage: bool = False, max_smem: int = 166912
    ) -> None:
        self.backend = "goldilocks_ntt_graph"
        self._two_stage = two_stage
        self.W = W
        self.L = L
        self.L0 = L0
        self.L1 = L1
        self.N = self.N_cyc = N_cyc
        self.lgN = (N_cyc - 1).bit_length()
        self.R = 1 << (W * L)

        tabs = _build_goldilocks_tables(N_cyc)
        self.inv_N = np.uint64(tabs["inv_N"])
        self.d_dif_tw = cp.asarray(tabs["dif_tw"])
        self.d_dit_tw = cp.asarray(tabs["dit_tw"])
        self.d_psi_pows = cp.asarray(tabs["psi_pows"])
        self.d_inv_psi_n = cp.asarray(tabs["inv_psi_n"])
        self._dit_outer_off = int(len(tabs["dit_tw"]) - 3 * (N_cyc >> 2))

        B_L0 = 1 << (W * L0)
        B_L1 = 1 << (W * L1)
        K_invs = []
        self.x0 = []
        for p in self.P:
            pinv = (-_modinv(p, self.R)) % self.R
            K_invs.append(((pinv + 1) // B_L0) % B_L1)
            self.x0.append(self.R % p)

        kinv_u32 = to_limbs_u32(K_invs, L1, W=W)
        p_u32 = to_limbs_u32(self.P, L, W=W)

        fkinv_pad = np.zeros((self.B, N_cyc), dtype=np.uint64)
        fkinv_pad[:, :L1] = kinv_u32
        fpsh_pad = np.zeros((self.B, N_cyc), dtype=np.uint64)
        for k in range(L):
            fpsh_pad[:, (k - L) % N_cyc] = p_u32[:, k]

        self.d_FKinv_ntt = self._batch_host_dif_prescaled(fkinv_pad, tabs, max_smem=max_smem)
        self.d_FPsh_ntt = self._batch_host_dif_prescaled(fpsh_pad, tabs, max_smem=max_smem)

        self.x0_u32 = to_limbs_u32(self.x0, L, W=W)
        self.xbuf = cp.asarray(self.x0_u32.copy())
        self.s_plus = cp.empty((self.B, N_cyc), dtype=cp.uint64)
        self.s_minus = cp.empty((self.B, N_cyc), dtype=cp.uint64)
        self.tlo_scratch = cp.empty((self.B, L), dtype=cp.uint32)

        mod = _get_goldilocks_module()
        self.k_inc = mod.get_function("inc_base_step")

        if not two_stage:
            self.k_sq = mod.get_function("goldilocks_sq_split")
            self.k_red = mod.get_function("goldilocks_proth_reduce")
            self.smem_sq = N_cyc * 8
            self.smem_red = N_cyc * 8 + N_cyc + 2048 + 32
            if self.smem_sq > 49152:
                self.k_sq.max_dynamic_shared_size_bytes = self.smem_sq
            if self.smem_red > 49152:
                self.k_red.max_dynamic_shared_size_bytes = self.smem_red
        else:
            self.d_work = cp.empty((self.B, N_cyc), dtype=cp.uint64)
            self.k_2s_prep = mod.get_function("gold_2s_prep_sq")
            self.k_2s_odif = mod.get_function("gold_2s_outer_dif")
            self.k_2s_sub = mod.get_function("gold_2s_sub_sq_or_mul")
            self.k_2s_odit = mod.get_function("gold_2s_outer_dit")
            self.k_2s_tlo = mod.get_function("gold_2s_tlo_norm")
            self.k_2s_m1q = mod.get_function("gold_2s_m1_q_norm")
            self.k_2s_cyc = mod.get_function("gold_2s_cyclic_reduce")

            self.smem_sq = (N_cyc >> 2) * 8
            self.smem_tlo = L * 4 + 2048
            self.smem_red = N_cyc * 4 + 2064
            if self.smem_sq > 49152:
                self.k_2s_sub.max_dynamic_shared_size_bytes = self.smem_sq
            if self.smem_tlo > 49152:
                self.k_2s_tlo.max_dynamic_shared_size_bytes = self.smem_tlo
                self.k_2s_m1q.max_dynamic_shared_size_bytes = self.smem_tlo
            if self.smem_red > 49152:
                self.k_2s_cyc.max_dynamic_shared_size_bytes = self.smem_red

        self._graph_head = None
        self._graph_tail = None
        self._build_cuda_graphs()

    @staticmethod
    def _batch_host_dif_prescaled(mat_u64: np.ndarray, tabs: dict[str, Any], *, max_smem: int = 166912) -> Any:
        """GPU-accelerated Radix-4 DIF precomputation across all B rows (< 0.2 ms)."""
        N = int(tabs["N_cyc"])
        lgN = int(tabs["lgN"])
        dif_tw = tabs["dif_tw"]
        inv_N = int(tabs["inv_N"])
        mod = _get_goldilocks_module()
        d_mat = cp.asarray(np.ascontiguousarray(mat_u64, dtype=np.uint64))
        d_tw = cp.asarray(dif_tw)
        B_rows = mat_u64.shape[0]
        smem = N * 8
        if smem <= max_smem:
            kern = mod.get_function("precompute_ntt_prescaled")
            if smem > 49152:
                kern.max_dynamic_shared_size_bytes = smem
            kern((B_rows,), (512,), (d_mat, d_tw, np.int32(N), np.int32(lgN), np.uint64(inv_N)), shared_mem=smem)
        else:
            Q = N >> 2
            k_odif = mod.get_function("gold_2s_outer_dif")
            k_sdif = mod.get_function("gold_2s_sub_dif_scale")
            sub_smem = Q * 8
            if sub_smem > 49152:
                k_sdif.max_dynamic_shared_size_bytes = sub_smem
            k_odif(((Q + 255) // 256, B_rows), (256,), (d_mat, d_tw, np.int32(N)))
            k_sdif((4, B_rows), (512,), (d_mat, d_tw, np.int32(N), np.int32(lgN), np.uint64(inv_N)), shared_mem=sub_smem)
        cp.cuda.Device().synchronize()
        return d_mat

    def _launch_goldilocks_step(self, sub_step: int, f_is_one: bool) -> None:
        if not self._two_stage:
            self.k_sq(
                (2, self.B),
                (512,),
                (
                    self.xbuf,
                    self.s_plus,
                    self.s_minus,
                    self.d_dif_tw,
                    self.d_dit_tw,
                    self.d_psi_pows,
                    self.d_inv_psi_n,
                    self.d_f_steps,
                    self.d_base_step,
                    np.int32(sub_step),
                    np.int32(1 if f_is_one else 0),
                    np.int32(self.B),
                    np.int32(self.L),
                    np.int32(self.W),
                    np.int32(self.N_cyc),
                    np.int32(self.lgN),
                    self.inv_N,
                ),
                shared_mem=self.smem_sq,
                stream=self.stream,
            )
            self.k_red(
                (self.B,),
                (512,),
                (
                    self.s_plus,
                    self.s_minus,
                    self.d_FKinv_ntt,
                    self.d_FPsh_ntt,
                    self.d_dif_tw,
                    self.d_dit_tw,
                    self.tlo_scratch,
                    self.xbuf,
                    self.overflow,
                    np.int32(self.L),
                    np.int32(self.L0),
                    np.int32(self.L1),
                    np.int32(self.W),
                    np.int32(self.N_cyc),
                    np.int32(self.lgN),
                ),
                shared_mem=self.smem_red,
                stream=self.stream,
            )
            return

        Q = self.N_cyc >> 2
        grid_q = ((Q + 255) // 256, self.B)
        s = self.stream

        self.k_2s_prep(
            ((self.N_cyc + 255) // 256, self.B),
            (256,),
            (
                self.xbuf, self.s_plus, self.s_minus, self.d_psi_pows,
                self.d_f_steps, self.d_base_step,
                np.int32(sub_step), np.int32(1 if f_is_one else 0),
                np.int32(self.B), np.int32(self.L), np.int32(self.W), np.int32(self.N_cyc),
            ),
            stream=s,
        )
        # Squaring s_plus (cyclic) and s_minus (negacyclic)
        self.k_2s_odif(grid_q, (256,), (self.s_plus, self.d_dif_tw, np.int32(self.N_cyc)), stream=s)
        self.k_2s_sub((4, self.B), (512,), (self.s_plus, self.s_plus, np.int32(1), self.d_dif_tw, self.d_dit_tw, np.int32(self.N_cyc), np.int32(self.lgN)), shared_mem=self.smem_sq, stream=s)
        self.k_2s_odit(grid_q, (256,), (self.s_plus, self.d_dit_tw, np.int32(self._dit_outer_off), self.d_inv_psi_n, self.inv_N, np.int32(1), np.int32(self.N_cyc)), stream=s)

        self.k_2s_odif(grid_q, (256,), (self.s_minus, self.d_dif_tw, np.int32(self.N_cyc)), stream=s)
        self.k_2s_sub((4, self.B), (512,), (self.s_minus, self.s_minus, np.int32(1), self.d_dif_tw, self.d_dit_tw, np.int32(self.N_cyc), np.int32(self.lgN)), shared_mem=self.smem_sq, stream=s)
        self.k_2s_odit(grid_q, (256,), (self.s_minus, self.d_dit_tw, np.int32(self._dit_outer_off), self.d_inv_psi_n, self.inv_N, np.int32(2), np.int32(self.N_cyc)), stream=s)

        # T_lo normalize -> m1 = T_lo[:L1] * K_inv -> q -> q * P_sh -> cyclic reduce
        self.k_2s_tlo((self.B,), (512,), (self.s_plus, self.s_minus, self.tlo_scratch, self.d_work, np.int32(self.L), np.int32(self.L1), np.int32(self.W), np.int32(self.N_cyc)), shared_mem=self.smem_tlo, stream=s)

        self.k_2s_odif(grid_q, (256,), (self.d_work, self.d_dif_tw, np.int32(self.N_cyc)), stream=s)
        self.k_2s_sub((4, self.B), (512,), (self.d_work, self.d_FKinv_ntt, np.int32(0), self.d_dif_tw, self.d_dit_tw, np.int32(self.N_cyc), np.int32(self.lgN)), shared_mem=self.smem_sq, stream=s)
        self.k_2s_odit(grid_q, (256,), (self.d_work, self.d_dit_tw, np.int32(self._dit_outer_off), self.d_inv_psi_n, self.inv_N, np.int32(0), np.int32(self.N_cyc)), stream=s)

        self.k_2s_m1q((self.B,), (512,), (self.d_work, self.tlo_scratch, np.int32(self.L), np.int32(self.L0), np.int32(self.L1), np.int32(self.W), np.int32(self.N_cyc)), shared_mem=self.smem_tlo, stream=s)

        self.k_2s_odif(grid_q, (256,), (self.d_work, self.d_dif_tw, np.int32(self.N_cyc)), stream=s)
        self.k_2s_sub((4, self.B), (512,), (self.d_work, self.d_FPsh_ntt, np.int32(0), self.d_dif_tw, self.d_dit_tw, np.int32(self.N_cyc), np.int32(self.lgN)), shared_mem=self.smem_sq, stream=s)
        self.k_2s_odit(grid_q, (256,), (self.d_work, self.d_dit_tw, np.int32(self._dit_outer_off), self.d_inv_psi_n, self.inv_N, np.int32(0), np.int32(self.N_cyc)), stream=s)

        self.k_2s_cyc((self.B,), (512,), (self.s_plus, self.s_minus, self.d_work, self.xbuf, self.overflow, np.int32(self.L), np.int32(self.W), np.int32(self.N_cyc)), shared_mem=self.smem_red, stream=s)

    def _init_cufft_gpu(self, bits: int, max_smem_optin: int) -> None:
        self.backend = "proth_cufft_graph"
        self.W = LIMB
        self.L = L = (bits + 5 + LIMB - 1) // LIMB
        self.L0 = L0 = self.n // LIMB
        self.L1 = L1 = L - L0
        self.R = 1 << (LIMB * L)

        self.N_cyc = nice_even_fft_size(L + 4)
        self.N = self.N_sq = max(self.N_cyc, nice_even_fft_size(2 * L + 2))
        self.N_inv = nice_even_fft_size(2 * L1 + 2)
        smem_cyc = self.N_cyc * 4 + 2048 + 64
        if smem_cyc > max_smem_optin:
            raise RuntimeError(f"N_cyc={self.N_cyc} cyclic SMEM {smem_cyc} exceeds {max_smem_optin}")

        B_L0 = 1 << (LIMB * L0)
        B_L1 = 1 << (LIMB * L1)
        K_invs = []
        self.x0 = []
        for p in self.P:
            pinv = (-_modinv(p, self.R)) % self.R
            K_invs.append(((pinv + 1) // B_L0) % B_L1)
            self.x0.append(self.R % p)

        kinv_f64 = to_limbs(K_invs, L1)
        p_f64 = to_limbs(self.P, L)
        psh_f64 = np.zeros((self.B, self.N_cyc), dtype=np.float64)
        for k in range(L):
            psh_f64[:, (k - L) % self.N_cyc] = p_f64[:, k]

        self.FKinv = cp.fft.rfft(cp.asarray(kinv_f64), n=self.N_inv, axis=1) * (1.0 / self.N_inv)
        self.FPsh = cp.fft.rfft(cp.asarray(psh_f64), n=self.N_cyc, axis=1) * (1.0 / self.N_cyc)

        self.x0_f64 = to_limbs(self.x0, L)
        self.xbuf = cp.asarray(self.x0_f64.copy())
        self.ybuf = cp.zeros((self.B, self.N_sq), dtype=cp.float64)
        self.X_sq = cp.empty((self.B, self.N_sq // 2 + 1), dtype=cp.complex128)
        self.T_raw = cp.empty((self.B, self.N_sq), dtype=cp.float64)
        self.tlo = cp.zeros((self.B, L), dtype=cp.float64)
        self.t1buf = cp.zeros((self.B, self.N_inv), dtype=cp.float64)
        self.R1_c = cp.empty((self.B, self.N_inv // 2 + 1), dtype=cp.complex128)
        self.m1_raw = cp.empty((self.B, self.N_inv), dtype=cp.float64)
        self.m1 = cp.zeros((self.B, L1), dtype=cp.float64)
        self.qbuf = cp.zeros((self.B, self.N_cyc), dtype=cp.float64)
        self.R2_c = cp.empty((self.B, self.N_cyc // 2 + 1), dtype=cp.complex128)
        self.qp_sh = cp.empty((self.B, self.N_cyc), dtype=cp.float64)
        self.rowflag = cp.zeros(self.B, dtype=cp.int32)

        # Build static cuFFT 1D batched plans bound to self.stream
        with self.stream:
            self.plan_sq_f = cufft.Plan1d(self.N_sq, cufft.CUFFT_D2Z, self.B)
            self.plan_sq_i = cufft.Plan1d(self.N_sq, cufft.CUFFT_Z2D, self.B)
            self.plan_inv_f = cufft.Plan1d(self.N_inv, cufft.CUFFT_D2Z, self.B)
            self.plan_inv_i = cufft.Plan1d(self.N_inv, cufft.CUFFT_Z2D, self.B)
            self.plan_cyc_f = cufft.Plan1d(self.N_cyc, cufft.CUFFT_D2Z, self.B)
            self.plan_cyc_i = cufft.Plan1d(self.N_cyc, cufft.CUFFT_Z2D, self.B)

        mod = _get_cufft_module()
        self.k_prep_y = mod.get_function("prep_y15")
        self.k_sq_scale = mod.get_function("cufft_sq_scale")
        self.k_cmul = mod.get_function("cufft_cmul_inplace")
        self.k_norm15 = mod.get_function("norm15_v4")
        self.k_res15 = mod.get_function("resolve15_v4")
        self.k_copy_t1 = mod.get_function("copy_tlo_prefix15")
        self.k_build_q = mod.get_function("build_proth_q15")
        self.k_fold_cyc = mod.get_function("fold_cyclic_resolve15")
        self.k_inc = mod.get_function("inc_base_step_cufft")

        self.smem_cyc = smem_cyc
        if self.smem_cyc > 49152:
            self.k_fold_cyc.max_dynamic_shared_size_bytes = self.smem_cyc

        self._graph_head = None
        self._graph_tail = None
        self._build_cuda_graphs()

    def _launch_cufft_step(self, sub_step: int, f_is_one: bool) -> None:
        L, L0, L1 = self.L, self.L0, self.L1
        n_freq_sq = self.N_sq // 2 + 1
        n_freq_inv = self.N_inv // 2 + 1
        n_freq_cyc = self.N_cyc // 2 + 1

        with self.stream:
            self.k_prep_y(
                ((L + 255) // 256, self.B),
                (256,),
                (
                    self.xbuf,
                    np.int64(L),
                    self.ybuf,
                    np.int64(self.N_sq),
                    self.d_f_steps,
                    self.d_base_step,
                    np.int32(sub_step),
                    np.int32(1 if f_is_one else 0),
                    np.int32(self.B),
                    np.int32(L),
                ),
            )
            self.plan_sq_f.fft(self.ybuf, self.X_sq, cufft.CUFFT_FORWARD)
            self.k_sq_scale(((n_freq_sq + 255) // 256, self.B), (256,), (self.X_sq, np.int32(n_freq_sq), np.float64(1.0 / self.N_sq)))
            self.plan_sq_i.fft(self.X_sq, self.T_raw, cufft.CUFFT_INVERSE)

            self.k_norm15(
                ((L + TILE - 1) // TILE, self.B),
                (TILE,),
                (self.T_raw, np.int64(self.N_sq), np.int32(L), self.tlo, np.int64(L), np.int32(L), self.maxerr, self.overflow, self.rowflag),
                shared_mem=2 * (TILE + HALO) * 8,
            )
            self.k_res15((self.B,), (1024,), (self.tlo, np.int64(L), np.int32(L), self.rowflag))
            self.k_copy_t1(((L1 + 255) // 256, self.B), (256,), (self.tlo, np.int64(L), self.t1buf, np.int64(self.N_inv), np.int32(L1)))

            self.plan_inv_f.fft(self.t1buf, self.R1_c, cufft.CUFFT_FORWARD)
            self.k_cmul(((n_freq_inv + 255) // 256, self.B), (256,), (self.R1_c, self.FKinv, np.int32(n_freq_inv)))
            self.plan_inv_i.fft(self.R1_c, self.m1_raw, cufft.CUFFT_INVERSE)

            self.k_norm15(
                ((L1 + TILE - 1) // TILE, self.B),
                (TILE,),
                (self.m1_raw, np.int64(self.N_inv), np.int32(L1), self.m1, np.int64(L1), np.int32(L1), self.maxerr, self.overflow, self.rowflag),
                shared_mem=2 * (TILE + HALO) * 8,
            )
            self.k_res15((self.B,), (1024,), (self.m1, np.int64(L1), np.int32(L1), self.rowflag))
            self.k_build_q((self.B,), (1024,), (self.tlo, np.int64(L), self.m1, np.int64(L1), self.qbuf, np.int64(self.N_cyc), np.int32(L), np.int32(L0), self.rowflag))

            self.plan_cyc_f.fft(self.qbuf, self.R2_c, cufft.CUFFT_FORWARD)
            self.k_cmul(((n_freq_cyc + 255) // 256, self.B), (256,), (self.R2_c, self.FPsh, np.int32(n_freq_cyc)))
            self.plan_cyc_i.fft(self.R2_c, self.qp_sh, cufft.CUFFT_INVERSE)

            self.k_fold_cyc(
                (self.B,),
                (512,),
                (
                    self.T_raw,
                    np.int64(self.N_sq),
                    np.int32(min(self.N_sq - 1, 2 * L)),
                    self.qp_sh,
                    np.int64(self.N_cyc),
                    np.int32(self.N_cyc),
                    self.xbuf,
                    np.int64(L),
                    np.int32(L),
                    self.maxerr,
                    self.overflow,
                ),
                shared_mem=self.smem_cyc,
            )

    def step_once(self, sub_step: int = 0, f_is_one: bool = True) -> None:
        if self.backend == "goldilocks_ntt_graph":
            self._launch_goldilocks_step(sub_step, f_is_one)
        else:
            self._launch_cufft_step(sub_step, f_is_one)

    def _build_cuda_graphs(self) -> None:
        G = self.graph_chunk
        # 1. Warmup 1 step outside stream capture so CuPy/cuFFT caches handles & pool blocks
        self.d_base_step.fill(0)
        self.step_once(0, f_is_one=False)
        self.stream.synchronize()
        self.reset_state()

        try:
            # 2. Capture Head Graph (G steps reading d_f_steps + incrementing d_base_step by G)
            self.stream.begin_capture()
            for s in range(G):
                self.step_once(s, f_is_one=False)
            self.k_inc((1,), (1,), (self.d_base_step, np.int32(G)), stream=self.stream)
            self._graph_head = self.stream.end_capture()

            # 3. Capture Tail Graph (G steps with f_is_one=True)
            self.stream.begin_capture()
            for s in range(G):
                self.step_once(s, f_is_one=True)
            self._graph_tail = self.stream.end_capture()
            self.stream.synchronize()
        except Exception:
            try:
                self.stream.end_capture()
            except Exception:
                pass
            self._graph_head = None
            self._graph_tail = None
        self.reset_state()

    def reset_state(self) -> None:
        self.d_base_step.fill(0)
        self.overflow.fill(0)
        self.maxerr.fill(0)
        if self.backend == "goldilocks_ntt_graph":
            self.xbuf[...] = cp.asarray(self.x0_u32)
        elif self.backend == "proth_cufft_graph":
            self.xbuf[...] = cp.asarray(self.x0_f64)
            self.rowflag.fill(0)
        self.stream.synchronize()

    def max_rounding_error(self) -> float:
        if self.backend in ("cpu", "goldilocks_ntt_graph") or self.B == 0:
            return 0.0
        return float(np.frombuffer(cp.asnumpy(self.maxerr).tobytes(), dtype=np.float32)[0])

    def _check(self) -> None:
        if self.backend == "cpu" or self.B == 0:
            return
        ov = int(cp.asnumpy(self.overflow)[0])
        if ov:
            raise RuntimeError(f"carry normalisation overflow flag {ov}")
        if self.max_rounding_error() > 0.2:
            raise RuntimeError("FFT rounding error above 0.2")

    def run(self, progress: Any = None, check_every: int = 4096) -> tuple[list[int], float]:
        """Return (list of exact Python int residues 2^((P_j-1)/2) mod P_j, max_rounding_error)."""
        if self.B == 0:
            return [], 0.0
        if self.backend == "cpu":
            assert self._cpu_eng is not None
            return self._cpu_eng.run(), 0.0

        self.reset_state()
        K = self.K0 + self.n - 1
        head_steps = min(K, self.K0 + 1)
        tail_steps = K - head_steps
        G = self.graph_chunk
        done = 0

        # Phase 1: Head steps (k = 0 .. head_steps - 1)
        if self._graph_head is not None and head_steps >= G:
            n_chunks = head_steps // G
            for c_idx in range(n_chunks):
                self._graph_head.launch(stream=self.stream)
                done += G
                if check_every and (done % check_every == 0):
                    self.stream.synchronize()
                    self._check()
                    if progress:
                        progress(done, K, self.max_rounding_error())
            rem_head = head_steps - n_chunks * G
        else:
            rem_head = head_steps

        if rem_head > 0:
            for s in range(rem_head):
                self.step_once(s, f_is_one=False)
            self.k_inc((1,), (1,), (self.d_base_step, np.int32(rem_head)), stream=self.stream)
            done += rem_head

        # Phase 2: Tail steps (k = K0 + 1 .. K - 1, where f == 1 identically!)
        if self._graph_tail is not None and tail_steps >= G:
            n_tchunks = tail_steps // G
            for _ in range(n_tchunks):
                self._graph_tail.launch(stream=self.stream)
                done += G
                if check_every and (done % check_every == 0):
                    self.stream.synchronize()
                    self._check()
                    if progress:
                        progress(done, K, self.max_rounding_error())
            rem_tail = tail_steps - n_tchunks * G
        else:
            rem_tail = tail_steps

        if rem_tail > 0:
            for s in range(rem_tail):
                self.step_once(s, f_is_one=True)
            done += rem_tail

        self.stream.synchronize()
        self._check()

        # Final Montgomery conversion: if K <= K0 (i.e. n == 1), f_final = 1 + mbits[K0 - 1], else 1
        xs = cp.asnumpy(self.xbuf)
        if self.n == 1 and self.K0 > 0:
            f_final = self.f_steps_host[self.K0]
        else:
            f_final = np.ones(self.B, dtype=np.uint8)

        out: list[int] = []
        for j, p in enumerate(self.P):
            if self.backend == "goldilocks_ntt_graph":
                v_limbs = from_limbs_u32(xs[j], W=self.W)
            else:
                v_limbs = from_limbs(xs[j])
            v_mont = (v_limbs * int(f_final[j])) % p
            out.append(int((v_mont * _modinv(self.R, p)) % p))
        return out, self.max_rounding_error()


BatchScreen = BatchScreenV4


def screen(
    spec: dict[str, Any],
    ts: Any,
    gmpy2: Any = None,
    progress: Any = None,
    *,
    backend: str = "auto",
) -> tuple[dict[int, bool], float, BatchScreenV4]:
    """Screen offsets `ts` of a desert.py spec; returns ({int(t): bool(r == 1)}, err, bs)."""
    m0 = int(spec["m0"])
    Mc = int(spec["Mc"])
    n = int(spec["n"])
    t_list = [int(t) for t in ts]
    ms = [m0 + t * Mc for t in t_list]
    bs = BatchScreenV4(n, ms, gmpy2=gmpy2, backend=backend)
    res, err = bs.run(progress=progress)
    return {int(t): bool(int(r) == 1) for t, r in zip(t_list, res)}, err, bs
