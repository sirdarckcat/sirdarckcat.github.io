"""ctypes wrapper of fm13.c: base-2 Fermat tests of numbers of up to 664 bits with AVX-512 IFMA (Intel Ice Lake / Sapphire
Rapids and later, AMD Zen 4 and later).  available() says whether this CPU has it; the library is compiled with gcc on first use."""
import ctypes
import hashlib
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "fm13.c")
HDR = os.path.join(HERE, "fm13_step.h")
NW = 11


def _flags():
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("flags"):
                return set(line.split(":", 1)[1].split())
    except OSError:
        pass
    return set()


def _outdir():
    import tempfile
    if os.access(HERE, os.W_OK):
        return HERE
    d = os.path.join(tempfile.gettempdir(), "fm13-%d" % os.getuid())
    os.makedirs(d, exist_ok=True)
    return d


def available():
    f = _flags()
    return {"avx512f", "avx512ifma", "avx512dq", "avx512bw", "avx512vl"} <= f


def build(force=False):
    tag = hashlib.sha1(("".join(l for l in open("/proc/cpuinfo") if l.startswith("model name"))).encode()).hexdigest()[:8]
    out = os.path.join(_outdir(), f"libfm13-{tag}.so")
    newest = max(os.path.getmtime(SRC), os.path.getmtime(HDR))
    if force or not os.path.exists(out) or os.path.getmtime(out) < newest:
        tmp = f"{out}.{os.getpid()}.tmp"
        subprocess.check_call(["gcc", "-O3", "-march=native", "-shared", "-fPIC", "-o", tmp, SRC])
        os.replace(tmp, out)
    return out


_LIB = None


def load():
    global _LIB
    if _LIB is None:
        lib = ctypes.CDLL(build())
        vp = ctypes.c_void_p
        lib.fm13_test.argtypes = [ctypes.c_int, vp, vp, vp]
        lib.fm13_members.argtypes = [vp, vp, vp, ctypes.c_int, vp, vp, vp, vp]
        lib.fm13_members.restype = ctypes.c_int64
        lib.fm13_lanes.restype = ctypes.c_int
        _LIB = lib
    return _LIB


def words(x):
    return np.frombuffer(int(x).to_bytes(8 * NW, "little"), dtype=np.uint64).copy()


class Members:
    """The Fermat loop of search.run_block for one progression N = N0 + k M with rows q (N - q)."""

    def __init__(self, N0, M, U):
        self.lib = load()
        self.N0 = words(N0)
        self.M = words(M)
        self.U = np.ascontiguousarray(U, dtype=np.uint32)

    def first_pass(self, kv, rows, offs):
        """kv: k of each member; rows (u16) and offs (i64, len(kv)+1): the CSR row lists.  Returns int32[len(kv)]: the position
        in its list of the first row whose number passes the base-2 Fermat test, or -1."""
        kv = np.ascontiguousarray(kv, dtype=np.uint64)
        rows = np.ascontiguousarray(rows, dtype=np.uint16)
        offs = np.ascontiguousarray(offs, dtype=np.int64)
        out = np.empty(len(kv), dtype=np.int32)
        self.lib.fm13_members(self.N0.ctypes.data, self.M.ctypes.data, self.U.ctypes.data, len(kv), kv.ctypes.data,
                              rows.ctypes.data, offs.ctypes.data, out.ctypes.data)
        return out
