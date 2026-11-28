#!/usr/bin/env python3
"""Compile CUDA source with NVRTC (as cupy.RawModule does) on a machine WITHOUT a GPU, and read the SASS the GPU would run.

    python3 sass.py gsieve_kernels.cuh --arch sm_80 --kernel s200g_sieve -D KLOG=19 -D LLOG=15 -D NTHREADS=512 \
            -D 'S200G_DYNSHARED(type,name)=extern __shared__ type name[]' [--sass out.sass] [--loops]

What it needs (none of it needs a GPU; all of it is on PyPI / Ubuntu):
    pip install --target T nvidia-cuda-nvrtc-cu12          # libnvrtc.so.12  (T/nvidia/cuda_nvrtc/lib)
    pip install --target T2 nvidia-cuda-nvcc-cu12          # T2/nvidia/cuda_nvcc/bin/ptxas (12.9: sm_80 ... sm_120)
    curl -O https://developer.download.nvidia.com/compute/cuda/redist/cuda_nvdisasm/linux-x86_64/cuda_nvdisasm-linux-x86_64-12.9.88-archive.tar.xz
    tar xf that                                            # .../bin/nvdisasm (12.9 decodes sm_120 too; Ubuntu's 12.0 stops at sm_90)
set NVRTC_LIB, NVDISASM and PTXAS to their paths (or edit DEFAULTS below).

It prints, per kernel: registers / local / shared bytes from ptxas -v, the instruction count by opcode, and with --loops the body of
every loop (a backward branch) by opcode.  Static counts are what they are: they say what is issued, not what is waited for.
"""
import argparse
import collections
import ctypes
import os
import re
import subprocess
import sys
import tempfile

DEFAULTS = {
    "NVRTC_LIB": "/tmp/claude-0/-home-user-sirdarckcat-github-io/b6b07341-7caa-5bed-9677-bea302b80c6e/scratchpad/cudatools/nvrtc_pkg/nvidia/cuda_nvrtc/lib/libnvrtc.so.12",
    "NVDISASM": "/tmp/claude-0/-home-user-sirdarckcat-github-io/b6b07341-7caa-5bed-9677-bea302b80c6e/scratchpad/cudatools/r129/cuda_nvdisasm-linux-x86_64-12.9.88-archive/bin/nvdisasm",
    "PTXAS": "/tmp/claude-0/-home-user-sirdarckcat-github-io/b6b07341-7caa-5bed-9677-bea302b80c6e/scratchpad/cudatools/nvcc_w/nvidia/cuda_nvcc/bin/ptxas",
}


def tool(name):
    return os.environ.get(name, DEFAULTS[name])


class Nvrtc:
    def __init__(self):
        self.lib = ctypes.CDLL(tool("NVRTC_LIB"))

    def _check(self, rc, prog=None):
        if rc:
            msg = ""
            if prog is not None:
                n = ctypes.c_size_t()
                self.lib.nvrtcGetProgramLogSize(prog, ctypes.byref(n))
                buf = ctypes.create_string_buffer(n.value)
                self.lib.nvrtcGetProgramLog(prog, buf)
                msg = buf.value.decode(errors="replace")
            raise RuntimeError(f"NVRTC error {rc}\n{msg}")

    def compile(self, src, arch="sm_80", opts=(), want="cubin"):
        """want: 'cubin' (arch = sm_XX) or 'ptx' (arch = compute_XX).  Returns bytes."""
        prog = ctypes.c_void_p()
        self._check(self.lib.nvrtcCreateProgram(ctypes.byref(prog), src.encode(), b"k.cu", 0, None, None))
        o = [f"--gpu-architecture={arch}", "-std=c++11"] + list(opts)
        arr = (ctypes.c_char_p * len(o))(*[x.encode() for x in o])
        rc = self.lib.nvrtcCompileProgram(prog, len(o), arr)
        self._check(rc, prog)
        n = ctypes.c_size_t()
        if want == "cubin":
            self._check(self.lib.nvrtcGetCUBINSize(prog, ctypes.byref(n)))
            buf = ctypes.create_string_buffer(n.value)
            self._check(self.lib.nvrtcGetCUBIN(prog, buf))
        else:
            self._check(self.lib.nvrtcGetPTXSize(prog, ctypes.byref(n)))
            buf = ctypes.create_string_buffer(n.value)
            self._check(self.lib.nvrtcGetPTX(prog, buf))
        self.lib.nvrtcDestroyProgram(ctypes.byref(prog))
        return buf.raw[:n.value]


def disassemble(cubin_bytes):
    with tempfile.NamedTemporaryFile(suffix=".cubin", delete=False) as f:
        f.write(cubin_bytes)
        path = f.name
    try:
        out = subprocess.run([tool("NVDISASM"), "-c", path], capture_output=True, text=True)
        if out.returncode:
            raise RuntimeError(out.stderr)
        return out.stdout
    finally:
        os.unlink(path)


def ptxas_info(ptx_bytes, arch):
    """registers, stack (local) and shared bytes the way ptxas -v reports them, per entry."""
    with tempfile.NamedTemporaryFile(suffix=".ptx", delete=False) as f:
        f.write(ptx_bytes)
        path = f.name
    try:
        exe = tool("PTXAS")
        r = subprocess.run([exe, f"-arch={arch}", "-v", "-O3", path, "-o", "/dev/null"], capture_output=True, text=True)
        return r.stderr
    finally:
        os.unlink(path)


def parse_sass(text):
    """{function: (instrs, labels)}: instrs = [(address, 'OPCODE.MODS operands')], labels = {'.L_x_12': index of the instruction after it}."""
    funcs = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"\s*\.text\.(\w+):", line)
        if m:
            cur = m.group(1)
            funcs[cur] = ([], {})
            continue
        if cur is None:
            continue
        m = re.match(r"\s*(\.L_x_\d+):", line)
        if m:
            funcs[cur][1][m.group(1)] = len(funcs[cur][0])
            continue
        m = re.match(r"\s*/\*([0-9a-f]{4})\*/\s+(.*?)\s*;?\s*(?:/\*.*)?$", line)
        if m:
            body = m.group(2).strip().rstrip(";").strip()
            if not body or body.startswith(".") or re.fullmatch(r"[0-9a-fx ]+", body):
                continue
            funcs[cur][0].append((int(m.group(1), 16), body))
    return funcs


def opcode(body):
    b = re.sub(r"^@!?U?P\w+\s+", "", body)
    return b.split()[0] if b.split() else ""


def loops(instrs, labels):
    """backward branches: (start index, end index) of every loop; BRA targets are labels like `(.L_x_12)."""
    out = []
    for i, (a, body) in enumerate(instrs):
        if opcode(body).startswith("BRA"):
            m = re.search(r"(\.L_x_\d+)", body)
            if m and m.group(1) in labels and labels[m.group(1)] <= i:
                out.append((labels[m.group(1)], i))
    return out


def summarise(name, instrs, labels, show_loops):
    c = collections.Counter(opcode(b).split(".")[0] for _, b in instrs)
    print(f"{name}: {len(instrs)} instructions;  " + "  ".join(f"{k} {v}" for k, v in c.most_common(14)))
    if show_loops:
        for s, e in sorted(set(loops(instrs, labels))):
            cc = collections.Counter(opcode(b).split(".")[0] for _, b in instrs[s:e + 1])
            print(f"   loop [{s},{e}]  {e - s + 1} instructions:  " + "  ".join(f"{k} {v}" for k, v in cc.most_common(12)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--arch", default="sm_80")
    ap.add_argument("--kernel", default=None)
    ap.add_argument("-D", dest="defs", action="append", default=[])
    ap.add_argument("--head", default="", help="text put before the source (e.g. typedefs)")
    ap.add_argument("--sass", default=None)
    ap.add_argument("--loops", action="store_true")
    ap.add_argument("--opt", action="append", default=[], help="extra NVRTC options")
    a = ap.parse_args()
    head = a.head
    for d in a.defs:
        if "=" in d:
            k, v = d.split("=", 1)
            head += f"#define {k} {v}\n"
        else:
            head += f"#define {d} 1\n"
    src = head + open(a.source).read()
    nv = Nvrtc()
    cubin = nv.compile(src, a.arch, a.opt, "cubin")
    sass = disassemble(cubin)
    if a.sass:
        open(a.sass, "w").write(sass)
    funcs = parse_sass(sass)
    for name, (instrs, labels) in funcs.items():
        if a.kernel and name != a.kernel:
            continue
        summarise(name, instrs, labels, a.loops)
    ptx = nv.compile(src, "compute_" + a.arch[3:], a.opt, "ptx")
    cur = None
    for line in ptxas_info(ptx, a.arch).splitlines():
        m = re.search(r"Compiling entry function '(\w+)'", line)
        if m:
            cur = m.group(1)
            continue
        if cur and (not a.kernel or cur == a.kernel) and ("Used" in line or "spill" in line):
            print(f"  ptxas {cur}: {line.split(':', 1)[-1].strip()}")


if __name__ == "__main__":
    main()
