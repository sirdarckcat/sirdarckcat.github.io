"""The large-prime stage of a deep sieve on a GPU (cupy): marks by primes above the tile (2^tile_log bits), bucketed by (row, tile) and applied to the tile's bitmap.
A prototype with a benchmark, bench_bigprimes.py; see gbig_kernels.cuh for the method.

    from gbig import BigStage, make_table
    st = BigStage(U, TAB, ks_log=25, rg=16)           # U: the rows (u32), TAB: [nP, 4] u32 = {s, M^-1 mod s, floor(M^-1 2^32 / s), c0} of the primes above the tile
    out = st.run_group(row0, nrows)                   # cupy u32 [nrows, 2^ks_log / 32]: bit j of row r is 0 iff a prime of TAB kills member j of row0 + r in the batch
"""
import math
import os

import numpy as np
import cupy as cp

from bigchunks import make_chunks

HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = open(os.path.join(HERE, "gbig_kernels.cuh")).read()
_KCACHE = {}


def _kernels(tile_log, ks_log, rg, ppt, stage_cap=8192, rcta=2, pack=False, hoist=False, gunroll=1, flush2=False, order=False, lean=()):
    key = (tile_log, ks_log, rg, ppt, stage_cap, rcta, bool(pack), bool(hoist), gunroll, bool(flush2), bool(order), tuple(lean))
    if key not in _KCACHE:
        head = (f"#define S200G_DYNSHARED(type, name) extern __shared__ type name[]\n#define TILE_LOG {tile_log}\n#define KS_LOG {ks_log}\n"
                f"#define RG {rg}\n#define PPT {ppt}\n#define STAGE_CAP {stage_cap}\n#define RCTA {rcta}\n#define RCTA_LOG {rcta.bit_length() - 1}\n" + ("#define BIN_PACK 1\n" if pack else "") + ("#define GEN_HOIST 1\n" if hoist else "") + (f"#define GEN_UNROLL {gunroll}\n" if gunroll > 1 else "") + ("#define GEN_FLUSH2 1\n" if flush2 else "") + ("#define GEN_ORDER 1\n" if order else "") + defines(lean))
        mod = cp.RawModule(code=head + _SRC)
        _KCACHE[key] = {n: mod.get_function(n) for n in ("gbig_gen", "gbig_gen_st", "gbig_apply")}
    return _KCACHE[key]


def lean_flags():
    """the options of the generate kernel set in the environment, as names ("#define NAME 1") or "NAME=VALUE" ("#define NAME VALUE"): DEEP_GEN_SCAN2 (shuffle scan), DEEP_GEN_RESV_LATE (late
    reservation), DEEP_GEN_MINRED (min-based reduction), DEEP_GEN_ONEPASS (one visit a pair: per-bin slots, no pass B; needs DEEP_GEN_HOIST=1) with DEEP_GEN_SLOT_C / DEEP_GEN_OVF_CAP (its slots a bin and
    overflow entries; defaults in gbig_kernels.cuh)"""
    env = os.environ
    out = tuple(n for n, v in (("GEN_SCAN2", "DEEP_GEN_SCAN2"), ("GEN_RESV_LATE", "DEEP_GEN_RESV_LATE"), ("GEN_MINRED", "DEEP_GEN_MINRED"), ("GEN_ONEPASS", "DEEP_GEN_ONEPASS")) if env.get(v, "0") == "1")
    if "GEN_ONEPASS" in out:
        assert env.get("DEEP_GEN_HOIST", "0") == "1", "DEEP_GEN_ONEPASS=1 needs DEEP_GEN_HOIST=1"
        out += tuple(f"{n}={int(env[v])}" for n, v in (("SLOT_C", "DEEP_GEN_SLOT_C"), ("OVF_CAP", "DEEP_GEN_OVF_CAP")) if v in env)
        if env.get("DEEP_GEN_LB"):                                              # "512,3": __launch_bounds__(512, 3) (3 CTAs of 512 threads an SM need <= 40 registers)
            a, b = (int(x) for x in env["DEEP_GEN_LB"].split(","))
            out += (f"GEN_LB=__launch_bounds__({a},{b})",)
    return out


def onepass_overflow(stage_cap, rcta, ntiles, slot_c):
    """expected overflow entries a CTA of the one-pass kernel: the CTA's rcta x ntiles bins each get ~Poisson(lam) marks, lam = (3/4 of stage_cap marks a CTA, the chunks' target) / bins; a bin's marks past
    slot_c go to the overflow list (OVF_CAP entries, then the slow whole-CTA fallback)"""
    lam = 0.75 * stage_cap / (rcta * ntiles)
    p, ex = math.exp(-lam), 0.0
    for k in range(1, int(lam + 20 * math.sqrt(lam) + 50)):
        p *= lam / k
        if k > slot_c:
            ex += (k - slot_c) * p
    return lam, rcta * ntiles * ex


def onepass_slots_for(stage_cap, rcta, ntiles, max_entries=1.0):
    """the smallest multiple of 5 slots a bin with at most max_entries overflow entries a CTA expected"""
    c = 5
    while onepass_overflow(stage_cap, rcta, ntiles, c)[1] > max_entries:
        c += 5
    return c


def defines(names):
    """the #define lines of lean_flags() entries"""
    return "".join(f"#define {n.replace('=', ' ')}\n" if "=" in n else f"#define {n} 1\n" for n in names)


def primes_between(lo, hi):
    """primes p with lo < p <= hi (numpy sieve; 2^28 takes a few seconds and 270 MB)"""
    s = np.ones(hi + 1, dtype=bool)
    s[:2] = False
    for i in range(2, int(hi ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    idx = np.nonzero(s)[0]
    return idx[np.searchsorted(idx, lo, side="right"):].astype(np.uint32)


def make_table(S, M=None, N0=None, k0=0, rng=None):
    """TAB [nP, 4] u32 for the primes S.  With M and N0 the true values (M^-1 mod s, c0 = (N0 M^-1 + k0) mod s: a Python loop, for tests); without them random
    values with the same distribution (a benchmark does not need the true roots: the roots of (row, prime) pairs are uniform in [0, s) either way)."""
    S = np.asarray(S, dtype=np.uint32)
    if M is not None:
        INV = np.array([pow(M % int(s), -1, int(s)) for s in S], dtype=np.uint32)
        C0 = np.array([(N0 * int(i) + k0) % int(s) for i, s in zip(INV, S)], dtype=np.uint32)
    else:
        rng = rng or np.random.default_rng(1)
        INV = (rng.random(S.size) * (S - 1)).astype(np.uint32) + 1
        C0 = (rng.random(S.size) * S).astype(np.uint32)
    INVP = ((INV.astype(np.uint64) << np.uint64(32)) // S.astype(np.uint64)).astype(np.uint32)
    return np.ascontiguousarray(np.stack([S, INV, INVP, C0], axis=1))


def expected_cap(S, tile_log, margin=1.08, pack=False, nchunks=0):
    """a bin capacity: the expected marks of a (row, tile) bin, tile_bits * sum 1/s, plus a margin and 6 standard deviations.  pack: the capacity in WORDS of a packed bin (3 words a group of 5 marks, the
    runs of the nchunks CTAs padded to whole groups: 3 words a chunk more, at most)"""
    e = (1 << tile_log) * float(np.sum(1.0 / S.astype(np.float64)))
    marks = e * margin + 6.0 * math.sqrt(e) + 64
    if pack:
        marks = marks * 0.6 + 3.0 * nchunks
    return int(math.ceil(marks / 32.0)) * 32


class BigStage:
    def __init__(self, U, TAB, ks_log=25, tile_log=19, rg=16, ppt=4, threads=256, cap=None, S=None, kernels=None, staged=False, rcta=2, stage_cap=8192, pack=False):
        """TAB: a numpy [nP, 4] table (copied to the device) or a cupy one that the caller rebuilds each batch (then pass S, the host array of its primes, for the capacity).
        staged: the staged generate kernel (gbig_gen_st: a CTA takes a chunk of primes and rcta rows, sorts the marks by bin in shared memory and writes whole runs; threads >= rcta x tiles)"""
        self.U = U.astype(cp.uint32) if isinstance(U, cp.ndarray) else cp.asarray(np.asarray(U, dtype=np.uint32))     # U may already be on the device (BatchFeeder passes its own)
        self.TAB = TAB if isinstance(TAB, cp.ndarray) else cp.asarray(np.ascontiguousarray(TAB, dtype=np.uint32))
        self.nP = int(self.TAB.shape[0])
        self.ks_log, self.tile_log, self.rg, self.ppt, self.threads = ks_log, tile_log, rg, ppt, threads
        self.ntiles = 1 << (ks_log - tile_log)
        self.nbins = rg * self.ntiles
        self.tile_words = (1 << tile_log) // 32
        self.staged, self.rcta, self.stage_cap = bool(staged), int(rcta), int(stage_cap)
        assert self.rcta >= 1 and self.rcta & (self.rcta - 1) == 0, "rcta must be a power of two"
        self.pack = bool(pack)
        assert not self.pack or (self.staged and tile_log <= 19), "packed bins (19-bit marks, 5 in 3 words) need the staged kernel and tiles of at most 2^19 bits"
        self.flush2 = self.staged and os.environ.get("DEEP_GEN_FLUSH2", "0") == "1"      # the flat flush of the staging buffer (gbig_kernels.cuh, GEN_FLUSH2); options of the staged kernel only
        self.order = self.staged and os.environ.get("DEEP_GEN_ORDER", "0") == "1"
        self.lean = lean_flags() if self.staged else ()        # the generate grid is (row slices, chunks): the slices of a chunk run together (GEN_ORDER)
        if self.staged and "GEN_ONEPASS" in self.lean:                   # one-pass slots sized for this geometry: too few and most CTAs fill the overflow list and take the slow fallback
            slot_c = next((int(n.split("=")[1]) for n in self.lean if n.startswith("SLOT_C=")), 40)
            lam, ent = onepass_overflow(self.stage_cap, self.rcta, self.ntiles, slot_c)
            assert ent <= 32.0 or os.environ.get("DEEP_GEN_SLOT_C_ANY", "0") == "1", (                        # a quarter of the list; DEEP_GEN_SLOT_C_ANY=1: the CPU tests that force overflow on purpose
                f"DEEP_GEN_ONEPASS: {slot_c} slots a bin for ~{lam:.0f} marks a bin a CTA (stage_cap {self.stage_cap}, rcta {self.rcta}, {self.ntiles} tiles) means ~{ent:.0f} overflow entries a CTA: "
                f"the 128-entry list fills and the CTAs write the slow way; set DEEP_GEN_SLOT_C={onepass_slots_for(self.stage_cap, self.rcta, self.ntiles)} (or a smaller stage_cap / more rows a CTA)")
        self.k = kernels if kernels is not None else _kernels(tile_log, ks_log, rg, ppt, self.stage_cap, self.rcta, self.pack, os.environ.get("DEEP_GEN_HOIST", "0") == "1", int(os.environ.get("DEEP_GEN_UNROLL", "1")), self.flush2, self.order, self.lean)
        if S is None:
            S = self.TAB[:, 0].get() if hasattr(self.TAB, "get") else self.TAB[:, 0]
        if self.staged:
            assert threads % 32 == 0 and threads >= self.rcta * self.ntiles, "the staged kernel needs a CTA of at least rcta x tiles threads (one thread a bin for the scan)"
            self.pstart = cp.asarray(make_chunks(S, ks_log, 0.75 * self.stage_cap / self.rcta))      # chunks of primes with ~3/4 of the staging buffer in marks
            self.nchunks = int(self.pstart.size) - 1
        else:
            self.nchunks = 0
        self.cap = cap or expected_cap(S, tile_log, pack=self.pack, nchunks=self.nchunks)
        assert self.cap % 4 == 0, "a bin must start 16-byte aligned (the apply loads 16 bytes at a time)"
        self.apply_smem = 4 * self.tile_words
        if self.apply_smem > 48 * 1024:
            self.k["gbig_apply"].max_dynamic_shared_size_bytes = self.apply_smem
        self.gcnt = cp.zeros(self.nbins + 1, dtype=cp.uint32)
        self.out = cp.empty(self.nbins * self.tile_words, dtype=cp.uint32)
        self._bins = None
        self.retries = 0

    def gen_grid(self, nrows):
        """the launch grid of gbig_gen_st for nrows rows: (chunks, row slices), or (row slices, chunks) with DEEP_GEN_ORDER=1"""
        ny = (nrows + self.rcta - 1) // self.rcta
        if self.order:
            assert self.nchunks <= 65535, "DEEP_GEN_ORDER=1 puts the chunks in the y dimension of the grid (at most 65,535)"
            return (ny, self.nchunks)
        return (self.nchunks, ny)

    def _bins_for(self, cap):
        need = self.nbins * cap
        assert need < (1 << 32), "bins index would overflow 32 bits: use fewer rows a group or a smaller cap"
        if self._bins is None or self._bins.size < need:
            self._bins = None
            self._bins = cp.empty(need, dtype=cp.uint32)
        return self._bins

    def gen_group(self, row0, nrows, timings=None, U=None, defer=None):
        """gbig_gen for rows row0 .. row0 + nrows - 1 (nrows <= rg), repeated with the capacity the demand asks for if a bin overflowed.  Leaves self.gcnt, the bins and self.cap
        for gbig_apply / the tile kernel; returns (event before, event after) when timings is a dict (the generate time is added to timings['gen']).
        defer: a device array of one u32 that the caller zeroed before the window.  Without it the host waits for the device after EVERY group to read the overflow flag gcnt[NBINS] (~80 round
        trips a window, each of which leaves the stream idle and, in an overlapped driver, needs the GIL back from the main thread).  With it the flag is OR-ed into `defer` by a one-word kernel and
        the call returns at once: the caller reads `defer` once after the window and, if it is set, repeats the window with defer=None (the tile kernel applies no bin of an overflowed group,
        so nothing stale is read meanwhile)."""
        assert 1 <= nrows <= self.rg
        U = self.U if U is None else U
        grid = (self.nP + self.threads * self.ppt - 1) // (self.threads * self.ppt)
        use_events = timings is not None
        while True:
            bins = self._bins_for(self.cap)
            self.gcnt[:] = 0
            if use_events:
                e0, e1 = cp.cuda.Event(), cp.cuda.Event()
                e0.record()
            if self.staged:
                self.k["gbig_gen_st"](self.gen_grid(nrows), (self.threads,),
                                      (U, self.TAB, self.pstart, np.int32(row0), np.int32(nrows), np.uint32(self.cap), self.gcnt, bins))
            else:
                self.k["gbig_gen"]((grid,), (self.threads,), (U, self.TAB, np.int32(self.nP), np.int32(row0), np.int32(nrows), np.uint32(self.cap), self.gcnt, bins))
            if use_events:
                e1.record()
            if defer is not None:
                defer |= self.gcnt[self.nbins:self.nbins + 1]
                if use_events:
                    e1.synchronize()
                    timings["gen"] = timings.get("gen", 0.0) + cp.cuda.get_elapsed_time(e0, e1)
                return bins
            if int(self.gcnt[self.nbins]) == 0:
                break
            need = int(self.gcnt[:self.nbins].max())                     # the demand of the fullest bin: the size that works
            if use_events:
                e1.synchronize()
                timings["gen_retry"] = timings.get("gen_retry", 0.0) + cp.cuda.get_elapsed_time(e0, e1)
            self.cap = int(math.ceil((need + 64) / 32.0)) * 32
            self.retries += 1
        if use_events:
            e1.synchronize()
            timings["gen"] = timings.get("gen", 0.0) + cp.cuda.get_elapsed_time(e0, e1)
        return bins

    def run_group(self, row0, nrows, timings=None):
        """marks of rows row0 .. row0 + nrows - 1 (nrows <= rg): returns the bit matrix [nrows, 2^ks_log / 32] (a view of an internal buffer, valid until the next call).
        timings: a dict that receives the ms of the generate and the apply kernels (all attempts' generate time is added to 'gen_retry')."""
        bins = self.gen_group(row0, nrows, timings)
        if timings is not None:
            e1, e2 = cp.cuda.Event(), cp.cuda.Event()
            e1.record()
        self.k["gbig_apply"]((nrows * self.ntiles,), (self.threads,), (self.gcnt, bins, np.uint32(self.cap), self.out), shared_mem=self.apply_smem)
        if timings is not None:
            e2.record(); e2.synchronize()
            timings["apply"] = timings.get("apply", 0.0) + cp.cuda.get_elapsed_time(e1, e2)
        return self.out[:nrows * self.ntiles * self.tile_words].reshape(nrows, self.ntiles * self.tile_words)

    def pass_a_ms(self, row0, nrows, reps=3):
        """ms of gbig_gen with cap = 0: every CTA counts its marks and reserves (pass A), finds the reservation too large and writes nothing (no pass B): the time of the visits
        and the counting.  gcnt is garbage afterwards (run_group zeroes it)."""
        grid = (self.nP + self.threads * self.ppt - 1) // (self.threads * self.ppt)
        bins = self._bins_for(self.cap)
        best = None
        for _ in range(reps):
            self.gcnt[:] = 0
            e0, e1 = cp.cuda.Event(), cp.cuda.Event()
            e0.record()
            if self.staged:
                self.k["gbig_gen_st"](self.gen_grid(nrows), (self.threads,),
                                      (self.U, self.TAB, self.pstart, np.int32(row0), np.int32(nrows), np.uint32(0), self.gcnt, bins))
            else:
                self.k["gbig_gen"]((grid,), (self.threads,), (self.U, self.TAB, np.int32(self.nP), np.int32(row0), np.int32(nrows), np.uint32(0), self.gcnt, bins))
            e1.record(); e1.synchronize()
            ms = cp.cuda.get_elapsed_time(e0, e1)
            best = ms if best is None else min(best, ms)
        return best

    def words(self, nrows):
        """the words of the bins of the last group's first nrows rows (the marks of an unpacked stage; 3 a group of 5 marks, padding included, of a packed one)"""
        return int(self.gcnt[:nrows * self.ntiles].astype(cp.uint64).sum())

    def marks(self, nrows):
        w = self.words(nrows)
        return w * 5 // 3 if self.pack else w                       # (a packed stage: the padding of the groups of 5 is counted as marks, < 1%)
