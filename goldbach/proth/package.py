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
\\    modulus (and is far larger than it), hence is composite.  The scan is
\\    a parforprime over all threads (it runs sequentially on a PARI built
\\    without threads); cnt checks that every prime q < g was visited.
\\ Fail-stop: gp carries on with the next line after an error, so every check
\\ sets a flag on its own line and die() quits with exit status 1 unless the
\\ flag is set; a PASSED line can only follow passing checks.
\\ Split runs, for big records: put e.g. "qlo = 2; qhi = 4000000;" in range.gp and
\\ run  gp -q range.gp crosscheck.gp  to scan only the primes in [qlo, qhi).
\\ A split run skips step 1 (add "cert = 1;" to keep it) and prints RANGE PASSED;
\\ the ranges' counts must add up to primepi(g - 1).
default(parisize, 2000000000);
die(s) = print("CROSSCHECK FAILED: ", s); quit(1);
ok = 0; N = eval(readstr("N.txt")[1]); ok = type(N) == "t_INT";
if (!ok, die("N.txt unreadable"));
g = %(g)d; rmax = %(rmax)d;
P = N - g;
full = type(qlo) == "t_POL" && type(qhi) == "t_POL";
if (type(qlo) == "t_POL", qlo = 2);
if (type(qhi) == "t_POL", qhi = g);
if (type(cert) == "t_POL", cert = full);
if (type(qlo) != "t_INT" || type(qhi) != "t_INT" || qlo < 2 || qhi > g || qlo >= qhi, die("need integers 2 <= qlo < qhi <= g"));
ok = 0; ok = isprime(g);
if (!ok, die("g not prime"));
ok = !cert; if (cert, c = primecert(P, 1); ok = c != 0);
if (!ok, die("no N-1 certificate: P not prime?"));
ok = !cert; if (cert, ok = primecertisvalid(c));
if (!ok, die("PARI rejects its N-1 certificate"));
if (cert, print("PARI N-1 (Pocklington-Lehmer) certificate for P = N - g: valid"));
ok = !cert; if (cert, ok = isprime(P));
if (!ok, die("isprime(P) = 0"));
if (cert, print("PARI isprime(P) = 1"));
ok = 0; PR = vecprod(primes([2, rmax])); ok = 1;
if (!ok, die("primorial failed"));
done = 0; cnt = 0; bad = 0; export(N, PR); parforprime(q = qlo, qhi - 1, gcd(N - q, PR) == 1, isbad, cnt++; if (isbad, bad++)); done = 1;
want = primepi(qhi - 1) - primepi(qlo - 1);
if (full, print("primes q < g scanned: ", cnt, "   (pi(g-1) = ", primepi(g - 1), ")"));
if (!full, print("primes q in [", qlo, ", ", qhi, ") scanned: ", cnt, "   (primepi difference = ", want, ")"));
print("complements N - q with no prime factor <= ", rmax, ": ", bad);
if (!done || bad != 0 || cnt != want, die("SCAN FAILED"));
ok = 0; ok = gcd(P, PR) == 1;
if (!ok, die("P has a small factor"));
if (full, print("CROSSCHECK PASSED: g(N) = ", g));
if (!full, print("RANGE PASSED: [", qlo, ", ", qhi, "), ", cnt, " primes, g = ", g));
"""


def main():
    src, out = sys.argv[1], sys.argv[2].rstrip("/")
    os.makedirs(out, exist_ok=True)
    rec = json.load(open(src))
    shutil.copy(src, f"{out}/record.json")
    tests = os.path.join(os.path.dirname(os.path.abspath(src)), "tests.jsonl")
    if os.path.exists(tests):                      # search telemetry (one line per PRP test)
        shutil.copy(tests, f"{out}/search_tests.jsonl")
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
        log = "".join(l for l in (r.stdout + r.stderr).splitlines(True)
                      if "new stack size" not in l)
        open(f"{out}/crosscheck.log", "w").write(log)
        print(log)
        # gp continues after an error, so the PASSED line alone is not enough:
        # also require exit status 0 and no error line ("***") in the log.
        assert r.returncode == 0 and "CROSSCHECK PASSED" in r.stdout and "***" not in log, \
            "PARI cross-check failed"
    sums = []
    for f in sorted(os.listdir(out)):
        if f != "SHA256SUMS":
            sums.append(hashlib.sha256(open(f"{out}/{f}", "rb").read()).hexdigest() + "  " + f)
    open(f"{out}/SHA256SUMS", "w").write("\n".join(sums) + "\n")
    print(f"packaged {out} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
