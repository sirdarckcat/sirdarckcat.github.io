#!/usr/bin/env python3
"""Turn a GPU-screen hit into a proven, packaged record.

    python3 gpu_hit.py run_dir t gpu_tests.jsonl [--gpu "A100 (Colab)"]
                       [--screen "how the hit was screened"] [--no-package]

run_dir holds spec.json and the CPU tests.jsonl (desert.py search layout),
and gpu_tests.jsonl is gpu_search.py's log, downloaded from the runtime.
The GPU verdict is never trusted: the hit t is re-proved here on the CPU
with desert.bls_prove and the spec's non-residue base. Then this script:
- merges both logs into run_dir/tests.jsonl, one line per distinct t;
- writes record.json in desert.search's format, plus a "search" note;
- runs package.py, which builds records/height_<digits>digit_g<g>/ with
  N.txt, verify.log, PARI crosscheck.gp/.log and SHA256SUMS.
--screen replaces the GPU screen note (e.g. for a hit screened by PFGW on a
CPU runtime), and --no-package stops after record.json.
"""
import json
import os
import subprocess
import sys
import time

from gmpy2 import mpz

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import desert  # noqa: E402


def read_log(path):
    out = {}
    if path and os.path.exists(path):
        for line in open(path):
            if line.strip():
                d = json.loads(line)
                out.setdefault(int(d["t"]), d)
    return out


def main():
    run_dir, t, gpu_log = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    opt = sys.argv[4:]
    gpu = opt[opt.index("--gpu") + 1] if "--gpu" in opt else "A100 (Colab)"
    screen = (opt[opt.index("--screen") + 1] if "--screen" in opt
              else f"GPU {gpu}: gpu_screen.py, 2^((P-1)/2) = 1 (mod P)")
    spec = json.load(open(f"{run_dir}/spec.json"))
    m = mpz(spec["m0"]) + t * mpz(spec["Mc"])
    P = (m << spec["n"]) + 1
    t0 = time.time()
    how = desert.bls_prove(P, spec["base"])        # raises unless proven
    print(f"t={t}: CPU proof in {time.time() - t0:.0f}s: {how}", flush=True)
    N = P + spec["g"]
    cpu, gpu_tests = read_log(f"{run_dir}/tests.jsonl"), read_log(gpu_log)
    merged = dict(cpu)
    for tt, d in gpu_tests.items():
        merged.setdefault(tt, d)
    merged[t] = dict(merged.get(t, {"t": t}), ok=True,
                     proved="desert.bls_prove (CPU)")
    with open(f"{run_dir}/tests.jsonl", "w") as fh:
        for tt in sorted(merged):
            fh.write(json.dumps(merged[tt]) + "\n")
    rec = {
        "game": "height (Game 1), Proth/BLS-certified full cover",
        "g": spec["g"], "Q": spec["Q"], "digits": len(str(N)),
        "n": spec["n"], "t": t, "base": spec["base"], "proof": how,
        "cover": spec["cover"], "m": str(m), "N": str(N),
        "tests_run": len(merged),
        "search": {"cpu_tests": len(cpu),
                   "gpu_tests": len(set(gpu_tests) - set(cpu)),
                   "screen": screen,
                   "proof": "desert.bls_prove on CPU, spec base"},
    }
    json.dump(rec, open(f"{run_dir}/record.json", "w"))
    if "--no-package" in opt:
        print(f"wrote {run_dir}/record.json (not packaged)", flush=True)
        return
    out = os.path.join(HERE, "..", "records",
                       f"height_{rec['digits']}digit_g{spec['g']}")
    subprocess.run([sys.executable, f"{HERE}/package.py",
                    f"{run_dir}/record.json", out], check=True)
    print(f"record: {os.path.normpath(out)}", flush=True)


if __name__ == "__main__":
    main()
