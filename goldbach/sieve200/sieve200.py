"""ctypes wrapper of sieve200.c: the block sieve of search.run_block as a C library.

    from sieve200 import Sieve200
    sv = Sieve200(N0, M, U, B=1_000_000, logK=15, exclude=cover_primes)
    counts, bits = sv.block(k0)        # counts: u16[K] alive rows per member, bits: u64[nU, K/64]
    alive = sv.alive(bits)             # bool[nU, K], the matrix search.run_block builds (for tests)

The library is compiled on first use with gcc (-O3 -march=native; set SIEVE200_MARCH to change, e.g. haswell, or "generic"
for no vector ISA at all).  The compiled file goes next to the source and is rebuilt when the source is newer.
"""
import ctypes
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sieve200.c")


def _cpu_tag():
    """short hash of this CPU's model and flags: a -march=native build is only valid on the CPU that made it"""
    import hashlib
    try:
        lines = [l for l in open("/proc/cpuinfo") if l.startswith(("model name", "flags"))][:2]
        return hashlib.sha1("".join(lines).encode()).hexdigest()[:8]
    except OSError:
        return "x"


def build(march=None, force=False):
    march = march or os.environ.get("SIEVE200_MARCH", "native")
    tag = march.replace("=", "_") + ("-" + _cpu_tag() if march == "native" else "")
    out = os.path.join(HERE, f"libsieve200_{tag}.so")
    if force or not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(SRC):
        flags = [] if march == "generic" else [f"-march={march}"]
        tmp = f"{out}.{os.getpid()}.tmp"
        subprocess.check_call(["gcc", "-O3", *flags, "-shared", "-fPIC", "-o", tmp, SRC])
        os.replace(tmp, out)                      # atomic: another process may be building or loading the same file
    return out


_LIBS = {}


def load(march=None):
    path = build(march)
    if path not in _LIBS:
        lib = ctypes.CDLL(path)
        u32p = ctypes.POINTER(ctypes.c_uint32)
        lib.s200_new.restype = ctypes.c_void_p
        lib.s200_new.argtypes = [ctypes.c_char_p, ctypes.c_char_p, u32p, ctypes.c_int, ctypes.c_uint32,
                                 ctypes.c_int, u32p, ctypes.c_int]
        lib.s200_free.argtypes = [ctypes.c_void_p]
        for f in ("s200_nprimes", "s200_nrows", "s200_block_log"):
            getattr(lib, f).restype = ctypes.c_int
            getattr(lib, f).argtypes = [ctypes.c_void_p]
        lib.s200_prime.restype = ctypes.c_uint32
        lib.s200_prime.argtypes = [ctypes.c_void_p, ctypes.c_int]
        lib.s200_bits_bytes.restype = ctypes.c_size_t
        lib.s200_bits_bytes.argtypes = [ctypes.c_void_p]
        lib.s200_block.restype = ctypes.c_int
        lib.s200_block.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_void_p]
        lib.s200_extract.restype = ctypes.c_long
        lib.s200_extract.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
                                     ctypes.c_void_p, ctypes.c_long, ctypes.c_void_p]
        lib.s200_extract_bitmaps.restype = None
        lib.s200_extract_bitmaps.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
                                             ctypes.c_void_p]
        _LIBS[path] = lib
    return _LIBS[path]


class Sieve200:
    def __init__(self, N0, M, U, B, logK=15, exclude=(), march=None):
        self.lib = load(march)
        U = np.ascontiguousarray(U, dtype=np.uint32)
        ex = np.ascontiguousarray(sorted(set(int(e) for e in exclude)), dtype=np.uint32)
        u32p = ctypes.POINTER(ctypes.c_uint32)
        self.ctx = self.lib.s200_new(("%x" % int(N0)).encode(), ("%x" % int(M)).encode(),
                                     U.ctypes.data_as(u32p), len(U), int(B), int(logK),
                                     ex.ctypes.data_as(u32p), len(ex))
        if not self.ctx:
            raise ValueError("s200_new failed (bad hex, B < 5, logK outside 9..26, or q * B >= 2^50)")
        self.nU = len(U)
        self.U = U
        self.B = int(B)
        self.logK = int(logK)
        self.K = 1 << self.logK
        self.words = self.K // 64
        self.nS = self.lib.s200_nprimes(self.ctx)

    def __del__(self):
        ctx = getattr(self, "ctx", None)
        if ctx:
            self.lib.s200_free(ctx)
            self.ctx = None

    def primes(self):
        return np.array([self.lib.s200_prime(self.ctx, i) for i in range(self.nS)], dtype=np.int64)

    def block(self, k0, counts=True, bits=None):
        """Sieve members k0 .. k0 + K - 1.  Returns (counts or None, bits)."""
        if bits is None:
            bits = np.empty((self.nU, self.words), dtype=np.uint64)
        cnt = np.empty(self.K, dtype=np.uint16) if counts else None
        rc = self.lib.s200_block(self.ctx, ctypes.c_uint64(int(k0)),
                                 cnt.ctypes.data if counts else None, bits.ctypes.data)
        if rc:
            raise MemoryError("s200_block")
        return cnt, bits

    def alive(self, bits):
        """The boolean matrix [nU, K] of a bit matrix (search.run_block's `alive`)."""
        b = bits.view(np.uint8).reshape(self.nU, self.K // 8)
        return np.unpackbits(b, axis=1, bitorder="little").astype(bool)

    def survivors(self, bits, js):
        """The alive rows of members js (offsets inside the block): (rows u16, offsets i64[len(js)+1]), member i has
        rows[offsets[i]:offsets[i+1]] in increasing order."""
        js = np.ascontiguousarray(js, dtype=np.uint32)
        offs = np.empty(len(js) + 1, dtype=np.int64)
        cap = len(js) * self.nU
        rows = np.empty(cap, dtype=np.uint16)
        n = self.lib.s200_extract(self.ctx, bits.ctypes.data, js.ctypes.data, len(js), rows.ctypes.data, cap,
                                  offs.ctypes.data)
        if n < 0:
            raise MemoryError("s200_extract")
        return rows[:n], offs

    def bitmaps(self, bits, js):
        """The alive rows of members js as u64[len(js), ceil(nU/64)] bitmaps (bit r of member i: row r alive)."""
        js = np.ascontiguousarray(js, dtype=np.uint32)
        out = np.empty((len(js), (self.nU + 63) // 64), dtype=np.uint64)
        self.lib.s200_extract_bitmaps(self.ctx, bits.ctypes.data, js.ctypes.data, len(js), out.ctypes.data)
        return out
