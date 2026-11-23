#!/usr/bin/env python3
"""A cost model of the Fermat step loop, from its SASS, fitted to the GPU session's timings.  No GPU needed (NVRTC + nvdisasm, see sass.py).

    python3 costmodel.py [--src goldbach/fermat661/cuda] [--fermat3 FILE.cu]

For each kernel the loop body is read from the SASS the GPU would run (NVRTC 12.9 + nvdisasm, as sass.py) and its instructions are split into
  * IMAD.WIDE.U32 (the multiplications):                  T_mul = n_wide x the cost of one IMAD.WIDE,
  * every other instruction of the integer datapath:       T_alu = the sum of their costs (uniform-datapath, branch and local-memory instructions left out),
and the cycles a step are modelled as

    T = max(T_mul, T_alu) + rho x min(T_mul, T_alu)           (rho = 0: complete overlap of the two; rho = 1: they simply add)

The costs are the GPU session's bench_pipes.py part 1 (scheduler cycles a warp instruction), IMAD.WIDE.U32 being the row "IMAD.WIDE+acc, 1 bump" minus the IADD3 that bumps
the operand: 4.15 (A100), 4.5 (L4), 2.53 (RTX PRO 6000).  (FERMAT28.md used 2.3 / 2.4 for the A100 / L4 until 2026-11-23: a transcription error of mine, and the first
prediction, +47% from the "w" steps, was wrong because of it.)  The measured tests/s are the GPU session's (128 threads a CTA).  One free parameter rho and an overall clock scale
are fitted for each GPU; cycles a step = SMs x 4 x clock x 32 / (655 steps x tests/s).

Result (see FERMAT28.md): on the A100 rho = 0.35 and the six timings (four step variants, fermat28's asm, and the older fermat3, a different algorithm) agree within 1.5% at an
effective clock of 1.38 GHz (nominal 1.41).  On the RTX PRO 6000 the measured cycles are 1.5-1.6 x the model's at the nominal 2.4 GHz: the card runs at ~1.5-1.65 GHz
(power-limited?) or something inside the kernel costs 50% more than in the benchmark; `measure_all.sh` samples the clock to tell.
"""
import argparse
import collections
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sass as S

# cycles a warp instruction occupies a scheduler (bench_pipes.py part 1, GPU session 2026-11-22 23:10Z)
COST = {
    "sm_80": {"WIDE": 4.15, "IADD3": 2.14, "IADD3.X": 1.0, "IMAD": 2.04, "SHF": 2.13, "LOP3": 2.14, "LEA": 2.1, "SEL": 2.14, "ISETP": 2.1, "MOV": 0.3, "HFMA2": 0.3, "*": 2.0},
    "sm_89": {"WIDE": 4.5, "IADD3": 2.14, "IADD3.X": 1.0, "IMAD": 2.04, "SHF": 2.13, "LOP3": 2.14, "LEA": 2.1, "SEL": 2.14, "ISETP": 2.1, "MOV": 0.3, "HFMA2": 0.3, "*": 2.0},
    "sm_120": {"WIDE": 2.53, "IADD3": 1.82, "IADD3.X": 1.0, "IADD": 1.82, "IMAD": 2.02, "SHF": 1.82, "LOP3": 1.6, "LEA": 1.82, "SEL": 1.6, "ISETP": 1.82, "MOV": 0.3, "HFMA2": 0.3, "*": 1.8},
}
# LOP3 correction (2026-11-23): the benchmark row "LOP3" (x = (x & a) ^ b, fixed a, b) was folded by ptxas to 15 LOP3 for the 32 chain-ops of a loop iteration (bench_pipes.py --check), so
# its 0.75 / 1.07 / 1.07 cycles a chain-op are 1.6 (sm_120) and 2.28 (sm_80 / 89: 2.0 for the 17 integer-pipe instructions of the loop) cycles a LOP3.  Used here: 1.6 and 2.14 (as IADD3).
SKIP = {"BRA", "BSSY", "BSYNC", "UMOV", "UIADD3", "UISETP", "UIMAD", "ULDC", "NOP", "YIELD", "LDL", "STL", "EXIT", "S2R", "CS2R", "LDC", "BAR", "WARPSYNC", "ULOP3", "USHF"}
# measured by the GPU session, tests/s, 128 threads a CTA (2026-11-23 00:17Z).  key: (gpu, variant)
MEASURED = {
    ("A100", "fermat3"): 6.94e6, ("A100", "s1 plain"): 6.95e6, ("A100", "s1 plain+w"): 7.55e6, ("A100", "s2 plain+w"): 7.51e6, ("A100", "s1r plain+w"): 7.63e6,
    ("A100", "s1r asm"): 6.95e6,
    ("L4", "fermat3"): 3.92e6, ("L4", "s1 plain"): 4.00e6, ("L4", "s1 plain+w"): 4.57e6, ("L4", "s1r plain+w"): 4.62e6,
    ("RTX", "fermat3"): 13.08e6, ("RTX", "s1 asm"): 22.85e6, ("RTX", "s1r plain+w"): 22.74e6, ("RTX", "s1r asm"): 23.39e6,
}
GPUS = {"A100": ("sm_80", 108, 1.41e9), "L4": ("sm_89", 58, 1.5e9), "RTX": ("sm_120", 188, 2.4e9)}   # L4: power-capped, 1.44-1.6 GHz; RTX: nominal, real clock unknown
STEPS = 655
HEAD = "typedef unsigned int u32;\ntypedef unsigned long long u64;\n"
FIT_EXCLUDE = {("RTX", "fermat3")}          # sm_120's fermat3 SASS is mostly MOV / HFMA2 (not understood), left out of the fit


def kernels(fc, fermat3):
    """label -> (source text, defines): the sources the GPU session ran (step file + fermat28_kernel.cuh as gpu_fermat28.source(); fermat3: its extracted CUDA, optional)"""
    kern = open(os.path.join(fc, "fermat28_kernel.cuh")).read()
    kern31 = open(os.path.join(fc, "fermat31_kernel.cuh")).read()

    def k28(step, defs=()):
        return (HEAD + open(os.path.join(fc, step)).read() + kern, list(defs))
    d = {
        "s1 plain": k28("fermat28_step_s1.cuh"),
        "s1 plain+w": k28("fermat28_step_s1w.cuh"),
        "s2 plain+w": k28("fermat28_step_w.cuh"),
        "s1r plain+w": k28("fermat28_step_s1rw.cuh"),
        "s1 asm": k28("fermat28_step_s1.cuh", ["FM28_ASM"]),
        "s1r asm": k28("fermat28_step_s1r.cuh", ["FM28_ASM"]),
        "fermat31": (HEAD + open(os.path.join(fc, "fermat31_step.cuh")).read() + kern31, []),
        "fermat30": (HEAD + open(os.path.join(fc, "fermat30_step.cuh")).read() + kern31, []),
    }
    if fermat3:
        d["fermat3"] = (open(fermat3).read(), [])
    return d


def loop_counts(text, defs, arch):
    nv = S.Nvrtc()
    src = "".join(f"#define {d} 1\n" for d in defs) + text
    funcs = S.parse_sass(S.disassemble(nv.compile(src, arch, [], "cubin")))
    name = [k for k in funcs][0]
    instrs, labels = funcs[name]
    lp = sorted(set(S.loops(instrs, labels)), key=lambda x: x[1] - x[0], reverse=True)[0]
    body = instrs[lp[0]:lp[1] + 1]
    c = collections.Counter()
    for _, b in body:
        op = S.opcode(b)
        if op.startswith("IMAD.WIDE"):
            c["WIDE"] += 1
        elif op.startswith("IADD3.X"):
            c["IADD3.X"] += 1
        else:
            c[op.split(".")[0]] += 1
    return len(body), c


def times(c, arch):
    cost = COST[arch]
    tm = c.get("WIDE", 0) * cost["WIDE"]
    ta = sum(n * cost.get(op, cost["*"]) for op, n in c.items() if op != "WIDE" and op not in SKIP)
    return tm, ta


def model(tm, ta, rho):
    return max(tm, ta) + rho * min(tm, ta)


def fit(pts):
    """pts: [(tm, ta, measured cycles at the nominal clock)] -> (rho, scale, spread): measured = scale x model(rho), least squares on the logs"""
    best = None
    for r100 in range(0, 101):
        rho = r100 / 100
        lr = [math.log(meas / model(tm, ta, rho)) for tm, ta, meas in pts]
        mu = sum(lr) / len(lr)
        err = math.sqrt(sum((x - mu) ** 2 for x in lr) / len(lr))
        if best is None or err < best[0] - 1e-12:
            best = (err, rho, math.exp(mu))
    return best[1], best[2], best[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(HERE, "..", "..", "fermat661", "cuda"), help="goldbach/fermat661/cuda (the step files and fermat28_kernel.cuh)")
    ap.add_argument("--fermat3", default=None, help="the CUDA source of the GPU session's fermat3 kernel (gpu_fermat3.py's text), to include it")
    a = ap.parse_args()
    ks = kernels(a.src, a.fermat3)
    for gpu, (arch, nsm, clk) in GPUS.items():
        print(f"==== {gpu} ({arch}, {nsm} SMs, nominal {clk / 1e9:.2f} GHz)")
        info = {}
        for label, (text, defs) in ks.items():
            n, c = loop_counts(text, defs, arch)
            tm, ta = times(c, arch)
            info[label] = (n, c.get("WIDE", 0), tm, ta)
        pts = []
        for label, (n, w, tm, ta) in info.items():
            if (gpu, label) in MEASURED and (gpu, label) not in FIT_EXCLUDE:
                pts.append((tm, ta, nsm * 4 * clk * 32 / (STEPS * MEASURED[(gpu, label)])))
        rho, scale, err = fit(pts)
        eff = clk / scale
        print(f"fit on {len(pts)} points: rho = {rho:.2f}; measured cycles at the nominal clock = {scale:.3f} x model, i.e. the model holds at an effective clock of {eff / 1e9:.2f} GHz; spread {100 * err:.1f}%")
        print(f"{'variant':12s} {'loop':>5s} {'IMAD.WIDE':>9s} {'T_mul':>6s} {'T_alu':>6s} | {'model':>6s} {'measured':>8s} {'meas/model':>10s} | {'tests/s measured':>16s} {'predicted':>10s}")
        for label, (n, w, tm, ta) in info.items():
            m = model(tm, ta, rho)
            pred = nsm * 4 * eff * 32 / (STEPS * m)
            meas = MEASURED.get((gpu, label))
            if meas:
                mc = nsm * 4 * clk * 32 / (STEPS * meas) / scale
                print(f"{label:12s} {n:5d} {w:9d} {tm:6.0f} {ta:6.0f} | {m:6.0f} {mc:8.0f} {mc / m:10.3f} | {meas / 1e6:15.2f}M {pred / 1e6:9.2f}M")
            else:
                print(f"{label:12s} {n:5d} {w:9d} {tm:6.0f} {ta:6.0f} | {m:6.0f} {'':>8s} {'':>10s} | {'(not measured)':>16s} {pred / 1e6:9.2f}M")
        print()


if __name__ == "__main__":
    main()
