"""Package a found record: copy record.json, write N.txt and a PARI/GP
cross-check script, run the standalone verifier and the PARI cross-check,
and write SHA256SUMS.

    python3 package.py <search_out_dir>/record.json records/<name>
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

GP = r"""\\ Independent PARI/GP cross-check (separate code path from verify.py).
\\   gp -q crosscheck.gp
\\ 1. P = N - g is prime: PARI's own N-1 (Pocklington-Lehmer) certificate,
\\    built and validated by PARI, plus PARI's default isprime().
\\ 2. Brute-force scan, not using the cover classes at all: for EVERY prime
\\    q < g, N - q shares a factor with the primorial of the largest cover
\\    modulus (and is far larger than it), hence is composite.
default(parisize, 2000000000);
N = eval(readstr("N.txt")[1]);
g = %(g)d; rmax = %(rmax)d;
P = N - g;
if (!isprime(g), error("g not prime"));
c = primecert(P, 1);
if (c == 0, error("no N-1 certificate: P not prime?"));
if (!primecertisvalid(c), error("PARI rejects its N-1 certificate"));
print("PARI N-1 (Pocklington-Lehmer) certificate for P = N - g: valid");
if (!isprime(P), error("isprime(P) = 0"));
print("PARI isprime(P) = 1");
PR = vecprod(primes([2, rmax]));
cnt = 0; bad = 0;
forprime(q = 2, g - 1, cnt++; if (gcd(N - q, PR) == 1, bad++));
print("primes q < g scanned: ", cnt, "   (pi(g-1) = ", primepi(g - 1), ")");
print("complements N - q with no prime factor <= ", rmax, ": ", bad);
if (bad > 0 || cnt != primepi(g - 1), error("SCAN FAILED"));
if (gcd(P, PR) != 1, error("P has a small factor"));
print("CROSSCHECK PASSED: g(N) = ", g);
"""


def main():
    src, out = sys.argv[1], sys.argv[2].rstrip("/")
    os.makedirs(out, exist_ok=True)
    rec = json.load(open(src))
    shutil.copy(src, f"{out}/record.json")
    open(f"{out}/N.txt", "w").write(rec["N"] + "\n")
    rmax = max(r for r, _ in rec["cover"])
    open(f"{out}/crosscheck.gp", "w").write(GP % {"g": rec["g"], "rmax": rmax})
    here = os.path.dirname(os.path.abspath(__file__))
    t0 = time.time()
    r = subprocess.run([sys.executable, f"{here}/verify.py", f"{out}/record.json"],
                       capture_output=True, text=True)
    open(f"{out}/verify.log", "w").write(r.stdout + r.stderr)
    print(r.stdout, r.stderr)
    assert r.returncode == 0, "verifier failed"
    if shutil.which("gp"):
        r = subprocess.run(["gp", "-q", "crosscheck.gp"], cwd=out,
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        open(f"{out}/crosscheck.log", "w").write(r.stdout + r.stderr)
        print(r.stdout, r.stderr)
        assert "CROSSCHECK PASSED" in r.stdout, "PARI cross-check failed"
    sums = []
    for f in sorted(os.listdir(out)):
        if f != "SHA256SUMS":
            sums.append(hashlib.sha256(open(f"{out}/{f}", "rb").read()).hexdigest() + "  " + f)
    open(f"{out}/SHA256SUMS", "w").write("\n".join(sums) + "\n")
    print(f"packaged {out} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
