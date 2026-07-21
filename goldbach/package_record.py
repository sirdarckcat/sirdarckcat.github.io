"""Package a search success into a fully verifiable record directory.

Usage: package_record.py found_line.json specs.json outdir/

found_line.json: one line from the search output (name, k, N, digits, g)
specs.json: the spec list used for the search (to recover cover/N0/M)

Produces in outdir/:
  record.json     - N, g, k, N0, M, cover, residual (reconstruction data)
  evidence.json   - per-offset compositeness witnesses for all q < g
  complement_cert.gp - PARI/GP ECPP certificate for N - g (primality proof)
  check_cert.log  - output of primecertisvalid on the certificate
"""

import json
import os
import subprocess
import sys

import verify_record


def package(found, spec, outdir):
    os.makedirs(outdir, exist_ok=True)
    record = {
        "name": found["name"], "N": found["N"], "digits": found["digits"],
        "g": found["g"], "k": found["k"], "N0": spec["N0"], "M": spec["M"],
        "Q": spec["Q"], "cover": spec["cover"], "residual": spec["residual"],
    }
    with open(f"{outdir}/record.json", "w") as f:
        json.dump(record, f, indent=1)

    ev = verify_record.verify(found["N"], found["g"], spec["cover"])
    with open(f"{outdir}/evidence.json", "w") as f:
        json.dump(ev, f, indent=1)
    print(f"evidence: {ev['offsets_checked']} offsets "
          f"(cong {ev['by_congruence']}, trial {ev['by_trial_division']}, "
          f"mr2 {ev['by_strong_base2']})")

    # ECPP certificate for the large prime complement
    comp = int(found["N"]) - found["g"]
    gp_script = (
        f'default(parisize, 512000000);\n'
        f'c = primecert({comp});\n'
        f'print("gen: ", type(c));\n'
        f'write("{outdir}/complement_cert.gp", c);\n'
        f'print("valid: ", primecertisvalid(c));\n'
    )
    r = subprocess.run(["gp", "-q"], input=gp_script,
                       capture_output=True, text=True, timeout=7200)
    with open(f"{outdir}/check_cert.log", "w") as f:
        f.write(r.stdout + r.stderr)
    print("gp:", r.stdout.strip()[-200:])


def main():
    found = json.load(open(sys.argv[1]))
    specs = json.load(open(sys.argv[2]))
    if isinstance(specs, dict):
        specs = [specs]
    spec = next(s for s in specs if s["name"] == found["name"])
    package(found, spec, sys.argv[3])


if __name__ == "__main__":
    main()
