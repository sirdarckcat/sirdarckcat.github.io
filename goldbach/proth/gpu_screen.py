"""GPU screening for Proth/BLS Goldbach deserts: batched 2^((P-1)/2) mod P.

For a batch of candidates P_t = 1 + 2^n (m0 + t*Mc) sharing n, compute
x_t = 2^((P_t - 1)/2) mod P_t on the GPU (CuPy, double-precision cuFFT).
P_t = 1 (mod 8), so a prime P_t gives x_t = (2/P_t) = 1 (Euler criterion),
and x_t == 1 is a probable-prime screen. Every hit must be re-proved on the
CPU by desert.bls_prove (with the spec's non-residue base); a base-2 Euler
pseudoprime fails there. A screening error costs search time or a CPU
check, never a wrong record.

Arithmetic:
- 15-bit limbs held in float64, convolutions by batched rfft/irfft, one
  row per candidate.
- Montgomery reduction with R = 2^(15 L) > 16 P, so values stay below 2P
  (< 4P after a doubling) and there is no conditional subtraction.
- The carry-out of the low half of T + mP is exactly 1 (both halves are
  normalised, nonzero, and sum to R). U = T_high + mP_high + 1 therefore
  never has to push a carry through a full-length chain.
- Carries are resolved by one fused kernel per product: five local rounds
  over shared-memory tiles with an 8-limb halo. It records the worst FFT
  rounding error and flags any limb left unnormalised.
"""
import math

import numpy as np

try:
    import cupy as cp
    import cupyx.scipy.fft as cfft
except ImportError:          # host-only helpers stay importable for tests
    cp = cfft = None

LIMB = 15
MASK = (1 << LIMB) - 1
TILE = 256
HALO = 8

_NORM_SRC = r"""
extern "C" __global__
void norm15(const double* __restrict__ src, const long long src_stride,
            const int n_src, double* __restrict__ dst,
            const long long dst_stride, const int n_dst,
            unsigned int* __restrict__ maxerr_bits, int* __restrict__ overflow,
            int* __restrict__ rowflag)
{
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
            if (v > 0x8000) atomicOr(overflow, 1);      // impossible by bounds
            if (v == 0x8000) rowflag[row] = 1;          // unresolved 0/1 carry
            d[i] = (double)v;
        }
    }
}

// After norm15 every limb is in [0, 2^15]; what is left is a 0/1 carry that
// may ripple through a run of 0x7FFF limbs of any length (this happens for
// structured operands such as Mont(1) = R mod P, whose low limbs are all
// 0x7FFF because P = 1 mod 2^n). One block per flagged row resolves it
// exactly by carry-lookahead: per-thread segment summaries (generate,
// propagate), a Kogge-Stone scan across segments, then a sequential apply.
// Rows that are not flagged return at once. The carry out of the top limb
// is dropped (that is the mod 2^(15 n) truncation).
extern "C" __global__
void resolve15(double* __restrict__ data, const long long stride, const int n,
               int* __restrict__ rowflag)
{
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
"""


def nice_fft_size(n):
    """Smallest 2^a 3^b 5^c >= n."""
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


def to_limbs(vals, L):
    """Python ints (each < 2^(15L)) -> float64 array (len(vals), L)."""
    nbytes = (LIMB * L + 7) // 8 + 1
    w = (1 << np.arange(LIMB, dtype=np.int64))
    out = np.empty((len(vals), L), dtype=np.float64)
    for j, v in enumerate(vals):
        v = int(v)
        assert 0 <= v < (1 << (LIMB * L)), "value does not fit in L limbs"
        b = np.frombuffer(v.to_bytes(nbytes, "little"), dtype=np.uint8)
        bits = np.unpackbits(b, bitorder="little")[: LIMB * L]
        out[j] = bits.reshape(L, LIMB).astype(np.int64) @ w
    return out


def from_limbs(row):
    """Normalised limb row (float64) -> Python int."""
    limbs = np.rint(np.asarray(row)).astype(np.int64)
    assert limbs.min() >= 0 and limbs.max() <= MASK, "row not normalised"
    bits = ((limbs[:, None] >> np.arange(LIMB)) & 1).astype(np.uint8).ravel()
    return int.from_bytes(np.packbits(bits, bitorder="little").tobytes(),
                          "little")


class BatchScreen:
    """2^((P_j-1)/2) mod P_j for P_j = 1 + 2^n * m_j, all on the GPU."""

    def __init__(self, n, ms, gmpy2):
        self.g = gmpy2
        self.n = int(n)
        self.ms = [gmpy2.mpz(m) for m in ms]
        self.P = [(m << self.n) + 1 for m in self.ms]
        bits = max(int(p.bit_length()) for p in self.P)
        self.L = L = (bits + 5 + LIMB - 1) // LIMB        # R = 2^(15L) > 16 P
        self.R = gmpy2.mpz(1) << (LIMB * L)
        self.N = N = nice_fft_size(2 * L + 2)
        self.B = len(self.P)
        Pinv = [(-gmpy2.invert(p, self.R)) % self.R for p in self.P]
        self.x0 = [self.R % p for p in self.P]             # Montgomery 1
        mod = cp.RawModule(code=_NORM_SRC)
        self.kern = mod.get_function("norm15")
        self.resolve = mod.get_function("resolve15")
        self.rowflag = cp.zeros(len(self.P), dtype=cp.int32)
        self.FP = cp.fft.rfft(cp.asarray(to_limbs(self.P, L)), n=N, axis=1)
        self.FPinv = cp.fft.rfft(cp.asarray(to_limbs(Pinv, L)), n=N, axis=1)
        # exponent bits of m_j, MSB first, padded to a common length
        K0 = max(int(m.bit_length()) for m in self.ms)
        mb = np.zeros((self.B, K0), dtype=np.uint8)
        for j, m in enumerate(self.ms):
            s = m.digits(2)
            mb[j, K0 - len(s):] = np.frombuffer(s.encode(), np.uint8) - 48
        self.mbits = cp.asarray(np.ascontiguousarray(mb.T))  # (K0, B)
        self.K0 = K0
        self.maxerr = cp.zeros(1, dtype=cp.uint32)
        self.overflow = cp.zeros(1, dtype=cp.int32)

    def _norm(self, src, n_src, n_dst):
        dst = cp.empty((self.B, n_dst), dtype=cp.float64)
        grid = ((n_dst + TILE - 1) // TILE, self.B)
        self.kern(grid, (TILE,),
                  (src, np.int64(src.shape[1]), np.int32(n_src), dst,
                   np.int64(n_dst), np.int32(n_dst), self.maxerr,
                   self.overflow, self.rowflag),
                  shared_mem=2 * (TILE + HALO) * 8)
        self.resolve((self.B,), (1024,),
                     (dst, np.int64(n_dst), np.int32(n_dst), self.rowflag))
        return dst

    def mont_sq(self, x, f):
        """Montgomery square of (f * x); x: (B, L) normalised limbs."""
        L, N = self.L, self.N
        X = cp.fft.rfft(x * f[:, None], n=N, axis=1)
        T = self._norm(cp.fft.irfft(X * X, n=N, axis=1), 2 * L, 2 * L + 1)
        M = cp.fft.irfft(cp.fft.rfft(T[:, :L], n=N, axis=1) * self.FPinv,
                         n=N, axis=1)
        m = self._norm(M, L, L)
        MP = self._norm(cp.fft.irfft(cp.fft.rfft(m, n=N, axis=1) * self.FP,
                                     n=N, axis=1), 2 * L, 2 * L + 1)
        U = T[:, L:2 * L + 1] + MP[:, L:2 * L + 1]
        U[:, 0] += 1.0
        return self._norm(U, L + 1, L)

    def mont_sq2(self, x, f):
        """Same result as mont_sq with about half the carry work.

        W = irfft(X^2 + FFT(m) FFT(P)) gives the raw coefficients of T + mP.
        That sum is an exact multiple of R, so its low half contributes the
        integer c = sum_{i<L} w_i 2^(15(i-L)) to the high half, and c can be
        read exactly from the top four low coefficients: the remaining tail
        is below 2^-28 while c is an integer. Then U = normalise(w_L + c,
        w_(L+1), ...) and T and mP are never normalised in full.
        """
        L, N = self.L, self.N
        X = cp.fft.rfft(x * f[:, None], n=N, axis=1)
        X2 = X * X
        TL = self._norm(cp.fft.irfft(X2, n=N, axis=1), L, L)
        M = cp.fft.irfft(cp.fft.rfft(TL, n=N, axis=1) * self.FPinv,
                         n=N, axis=1)
        m = self._norm(M, L, L)
        W = cp.fft.irfft(X2 + cp.fft.rfft(m, n=N, axis=1) * self.FP,
                         n=N, axis=1)
        lo = cp.rint(W[:, L - 4:L])                     # positions L-4 .. L-1
        c = cp.rint(lo[:, 3] * 2.0 ** -15 + lo[:, 2] * 2.0 ** -30
                    + lo[:, 1] * 2.0 ** -45 + lo[:, 0] * 2.0 ** -60)
        H = W[:, L:2 * L].copy()        # raw high half; _norm rounds + checks
        H[:, 0] += c                    # c is an integer: rint(w + c) = rint(w) + c
        return self._norm(H, L, L)

    # v2 is the default from the 1e7 rung on. It was validated exactly
    # (gpu_validate_v2.py): residues equal gmpy2's at 120/3k/20k bits, the
    # 2e6 spec gives F/T/F, and the eight known 1.2e6 primes pass while
    # their 16 neighbours fail. It is 1.11-1.12x faster (gpu_bench_v2.py).
    use_v2 = True
    # v3 (mont_sq3) is v2's arithmetic without the padding/output copies, and the
    # default from the 16,045,849 rung on. gpu_validate_v3.py: its state is bit-for-bit
    # v2's after every one of 40-64 squarings at the 5e6, 1e7 and 16M rung sizes
    # (random f = 1/2 pattern); residues equal gmpy2's at 120/3k/20k bits; the 2e6 spec
    # gives F/T/F and the eight known 1.2e6 primes pass while their 16 neighbours fail.
    # 1.11-1.13x faster than v2 (measured on the A100 while it ran the 1e7 rung).
    use_v3 = True

    def _norm_into(self, src, src_stride, n_src, dst, dst_stride, n_dst):
        """_norm, but reading rows of stride src_stride (src may be a column
        view) and writing the first n_dst columns of a strided buffer."""
        grid = ((n_dst + TILE - 1) // TILE, self.B)
        self.kern(grid, (TILE,),
                  (src, np.int64(src_stride), np.int32(n_src), dst,
                   np.int64(dst_stride), np.int32(n_dst), self.maxerr,
                   self.overflow, self.rowflag),
                  shared_mem=2 * (TILE + HALO) * 8)
        self.resolve((self.B,), (1024,),
                     (dst, np.int64(dst_stride), np.int32(n_dst), self.rowflag))

    def mont_sq3(self, f2):
        """mont_sq2's arithmetic without its memory copies.

        x lives in the first L columns of the zero-padded (B, N) buffer xbuf
        (likewise TL in tbuf and m in mbuf), so no forward FFT pads; two of
        the three C2R transforms run in place; the high half of W is
        normalised straight from W into xbuf. The factor f (1 or 2) is
        applied as f^2 to X*X: FFT(f x) = f FFT(x) and (fX)^2 = f^2 X^2
        exactly for a power of two, so every value matches mont_sq2's.
        """
        L, N = self.L, self.N
        X = cfft.rfft(self.xbuf, n=N, axis=1)
        cp.multiply(X, X, out=X)
        X *= f2[:, None]
        T = cfft.irfft(X, n=N, axis=1)                 # X is still needed
        self._norm_into(T, N, L, self.tbuf, N, L)
        del T
        R1 = cfft.rfft(self.tbuf, n=N, axis=1)
        R1 *= self.FPinv
        M = cfft.irfft(R1, n=N, axis=1, overwrite_x=True)
        del R1
        self._norm_into(M, N, L, self.mbuf, N, L)
        del M
        R2 = cfft.rfft(self.mbuf, n=N, axis=1)
        R2 *= self.FP
        R2 += X
        del X
        W = cfft.irfft(R2, n=N, axis=1, overwrite_x=True)
        del R2
        lo = cp.rint(W[:, L - 4:L])
        c = cp.rint(lo[:, 3] * 2.0 ** -15 + lo[:, 2] * 2.0 ** -30
                    + lo[:, 1] * 2.0 ** -45 + lo[:, 0] * 2.0 ** -60)
        W[:, L] += c
        self._norm_into(W[:, L:], N, L, self.xbuf, N, L)

    def run(self, progress=None, check_every=4096):
        """Return (list of residues 2^((P-1)/2) mod P, max rounding error)."""
        f = cp.ones(self.B, dtype=cp.float64)
        K = self.K0 + self.n - 1
        zero = cp.zeros(self.B, dtype=cp.float64)
        if self.use_v3:
            self.xbuf = cp.zeros((self.B, self.N), dtype=cp.float64)
            self.tbuf = cp.zeros((self.B, self.N), dtype=cp.float64)
            self.mbuf = cp.zeros((self.B, self.N), dtype=cp.float64)
            self.xbuf[:, :self.L] = cp.asarray(to_limbs(self.x0, self.L))
            f2 = cp.ones(self.B, dtype=cp.float64)
            for k in range(K):
                self.mont_sq3(f2)
                if k < self.K0:
                    mb = self.mbits[k].astype(cp.float64)
                    f, f2 = 1.0 + mb, 1.0 + 3.0 * mb
                else:
                    f, f2 = zero + 1.0, zero + 1.0
                if check_every and (k + 1) % check_every == 0:
                    self._check()
                    if progress:
                        progress(k + 1, K, self.max_rounding_error())
            x = self.xbuf[:, :self.L]
        else:
            x = cp.asarray(to_limbs(self.x0, self.L))
            sq = self.mont_sq2 if self.use_v2 else self.mont_sq
            for k in range(K):
                x = sq(x, f)
                f = 1.0 + (self.mbits[k].astype(cp.float64) if k < self.K0
                           else zero)
                if check_every and (k + 1) % check_every == 0:
                    self._check()
                    if progress:
                        progress(k + 1, K, self.max_rounding_error())
        self._check()
        xs = cp.asnumpy(x)
        fs = cp.asnumpy(f)
        out = []
        for j, p in enumerate(self.P):
            v = (from_limbs(xs[j]) * int(fs[j])) % p      # Mont form
            out.append(int(v * self.g.invert(self.R, p) % p))
        return out, self.max_rounding_error()

    def max_rounding_error(self):
        return float(np.frombuffer(cp.asnumpy(self.maxerr).tobytes(),
                                   dtype=np.float32)[0])

    def _check(self):
        ov = int(cp.asnumpy(self.overflow)[0])
        if ov:
            raise RuntimeError(f"carry normalisation overflow flag {ov}")
        if self.max_rounding_error() > 0.2:
            raise RuntimeError("FFT rounding error above 0.2")


def screen(spec, ts, gmpy2, progress=None):
    """Screen offsets ts of a desert.py spec; returns {t: passes}."""
    m0, Mc, n = gmpy2.mpz(spec["m0"]), gmpy2.mpz(spec["Mc"]), spec["n"]
    ms = [m0 + int(t) * Mc for t in ts]
    bs = BatchScreen(n, ms, gmpy2)
    res, err = bs.run(progress=progress)
    return {int(t): (r == 1) for t, r in zip(ts, res)}, err, bs
