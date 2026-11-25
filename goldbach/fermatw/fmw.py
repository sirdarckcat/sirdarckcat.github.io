"""ctypes wrapper of fmw.c: base-2 Fermat tests of numbers of up to 52 L - 12 bits with AVX-512 IFMA, L limbs of 52 bits
(fm13 of ../fermat661 for any L).  limbs_for(bits) is the smallest L that holds a number of that many bits; lib(L) compiles
fmw.c for L (gen_fmw.py writes the step header) with gcc on first use and returns the loaded library."""
import ctypes
import hashlib
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "fmw.c")
GEN = os.path.join(HERE, "gen_fmw.py")
VARIANT = os.environ.get("FMW_VARIANT")             # default: win2 for L >= 21, win below (bench_ab.py)
GROUPS = int(os.environ.get("FMW_GROUPS", "1"))


def _flags():
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("flags"):
                return set(line.split(":", 1)[1].split())
    except OSError:
        pass
    return set()


def available():
    return {"avx512f", "avx512ifma", "avx512dq", "avx512bw", "avx512vl"} <= _flags()


def limbs_for(bits):
    L = 1
    while 52 * L - 12 < bits:
        L += 1
    return L


def _outdir():
    import tempfile
    if os.access(HERE, os.W_OK):
        return HERE
    d = os.path.join(tempfile.gettempdir(), "fmw-%d" % os.getuid())
    os.makedirs(d, exist_ok=True)
    return d


def default_variant(L):
    """win below 21 limbs, win2 for 21..47, loop (fmwl2_step.h, product scanning in register column blocks) from 48 on, where the
    straight-line steps stop paying (bench_ab.py / the loop A/B in README)"""
    return VARIANT or ("loop" if L >= 48 else "win2" if L >= 21 else "win")


def build(L, variant=None, groups=None, force=False):
    variant = variant or default_variant(L)
    groups = groups or GROUPS
    tag = hashlib.sha1(("".join(l for l in open("/proc/cpuinfo") if l.startswith("model name"))).encode()).hexdigest()[:8]
    d = _outdir()
    hdr = f"fmw_step_L{L}_{variant}_g{groups}.h"
    out = os.path.join(d, f"libfmw-L{L}-{variant}-g{groups}-{tag}.so")
    if variant == "loop":                                  # no generated header: the loop step is one file for every L
        loop_hdr = os.path.join(HERE, "fmwl2_step.h")
        if force or not os.path.exists(out) or os.path.getmtime(out) < max(os.path.getmtime(SRC), os.path.getmtime(loop_hdr)):
            tmp = f"{out}.{os.getpid()}.tmp"
            subprocess.check_call(["gcc", "-O3", "-march=native", "-shared", "-fPIC", f"-DFMW_L={L}", '-DFMW_HDR="fmwl2_step.h"',
                                   "-I", HERE, "-o", tmp, SRC])
            os.replace(tmp, out)
        return out
    newest = max(os.path.getmtime(SRC), os.path.getmtime(GEN))
    if force or not os.path.exists(out) or os.path.getmtime(out) < newest:
        tmpdir = os.path.join(d, f".build-{os.getpid()}")
        os.makedirs(tmpdir, exist_ok=True)
        subprocess.check_call([sys.executable, GEN, str(L), str(groups), variant], cwd=tmpdir, stdout=subprocess.DEVNULL)
        os.replace(os.path.join(tmpdir, f"fmw_step_L{L}.h"), os.path.join(tmpdir, hdr))
        tmp = f"{out}.{os.getpid()}.tmp"
        subprocess.check_call(["gcc", "-O3", "-march=native", "-shared", "-fPIC", f"-DFMW_L={L}", f'-DFMW_HDR="{hdr}"',
                               "-I", tmpdir, "-o", tmp, SRC])
        os.replace(tmp, out)
        os.remove(os.path.join(tmpdir, hdr))
        os.rmdir(tmpdir)
    return out


_LIBS = {}


def lib(L, variant=None, groups=None):
    key = (L, variant or default_variant(L), groups or GROUPS)
    if key not in _LIBS:
        h = ctypes.CDLL(build(L, variant, groups))
        vp = ctypes.c_void_p
        h.fmw_test.argtypes = [ctypes.c_int, vp, vp, vp]
        h.fmw_members.argtypes = [vp, vp, vp, ctypes.c_int, vp, vp, vp, vp]
        h.fmw_members.restype = ctypes.c_int64
        for f in ("fmw_lanes", "fmw_limbs", "fmw_words", "fmw_maxbits"):
            getattr(h, f).restype = ctypes.c_int
        assert h.fmw_limbs() == L
        _LIBS[key] = h
    return _LIBS[key]


def words(x, nw):
    return np.frombuffer(int(x).to_bytes(8 * nw, "little"), dtype=np.uint64).copy()


def test(ns, L=None, want_y=False):
    """Base-2 Fermat verdicts (uint8) of the numbers ns (odd, > 1, at most 52 L - 12 bits); optionally the residues y < 4n."""
    L = L or limbs_for(max(int(n).bit_length() for n in ns))
    h = lib(L)
    nw = h.fmw_words()
    buf = np.concatenate([words(n, nw) for n in ns])
    vd = np.zeros(len(ns), dtype=np.uint8)
    y = np.zeros(len(ns) * nw, dtype=np.uint64) if want_y else None
    h.fmw_test(len(ns), buf.ctypes.data, vd.ctypes.data, y.ctypes.data if want_y else None)
    if want_y:
        ys = [int.from_bytes(y[i * nw:(i + 1) * nw].tobytes(), "little") for i in range(len(ns))]
        return vd, ys
    return vd


class Members:
    """The Fermat loop of search.run_block for one progression N = N0 + k M with rows q (numbers N - q), as fm13.Members."""

    def __init__(self, N0, M, U, kmax):
        bits = (int(N0) + int(kmax) * int(M)).bit_length()
        self.L = limbs_for(bits)
        self.lib = lib(self.L)
        nw = self.lib.fmw_words()
        self.N0 = words(N0, nw)
        self.M = words(M, nw)
        self.U = np.ascontiguousarray(U, dtype=np.uint32)

    def first_pass(self, kv, rows, offs):
        kv = np.ascontiguousarray(kv, dtype=np.uint64)
        rows = np.ascontiguousarray(rows, dtype=np.uint16)
        offs = np.ascontiguousarray(offs, dtype=np.int64)
        out = np.empty(len(kv), dtype=np.int32)
        self.lib.fmw_members(self.N0.ctypes.data, self.M.ctypes.data, self.U.ctypes.data, len(kv), kv.ctypes.data,
                             rows.ctypes.data, offs.ctypes.data, out.ctypes.data)
        return out
