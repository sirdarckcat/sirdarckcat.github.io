#!/usr/bin/env python3
"""Generate an ECPP certificate for N - q with PARI/GP and assemble the final
JSON record package.

Usage: make_cert.py --cover cover.json --t T --q Q --out pkg.json \
                    [--claims '{"q_exceeds":105667, "digits_at_most":199}']
Runs: gp primecert  (and isprime(...,2) APR-CL as an independent algorithm),
then re-verifies the certificate with the pure-Python checker before writing.
"""
import argparse, json, subprocess, sys, os, hashlib
import gmpy2
from gmpy2 import mpz

def crt(classes):
    M = mpz(1); N0 = mpz(0)
    for r, b in classes:
        r = mpz(r); b = mpz(b)
        g = gmpy2.invert(M % r, r)
        N0 = N0 + M * ((b - N0) % r * g % r)
        M *= r
    return N0 % M, M

def pari_tokens_to_json(s):
    """Parse a GP-printed nested vector like [[a,b,[c,d]],...] into Python."""
    s = s.strip().replace(" ", "").replace("\n", "")
    out, stack, num = None, [], ""
    cur = None
    for ch in s:
        if ch == "[":
            new = []
            if stack: stack[-1].append(new)
            stack.append(new)
        elif ch in ",]":
            if num:
                stack[-1].append(int(num)); num = ""
            if ch == "]":
                cur = stack.pop()
        elif ch in "-0123456789":
            num += ch
        else:
            raise ValueError(f"unexpected char {ch!r}")
    return cur

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cover", required=True)
    ap.add_argument("--t", type=int, required=True)
    ap.add_argument("--q", type=int, required=True)
    ap.add_argument("--claims", default="{}")
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-aprcl", action="store_true")
    a = ap.parse_args()
    cov = json.load(open(a.cover))
    classes = [(int(r), int(b)) for r, b in cov["classes"]]
    N0, M = crt([(2, 0)] + classes)
    N = N0 + a.t * M
    P = N - a.q
    assert N % 2 == 0
    assert gmpy2.is_bpsw_prp(P) and gmpy2.is_strong_prp(P, 2), "P not even a PRP?!"
    print(f"N: {len(str(N))} digits; certifying P = N - {a.q} ({len(str(P))} digits)")
    work = os.path.dirname(os.path.abspath(a.out)) or "."
    pf = os.path.join(work, f"P_{a.q}.txt")
    open(pf, "w").write(str(P))
    gp = f'''
default(parisizemax, 8G);
P = eval(readstr("{pf}")[1]);
c = primecert(P);
if (c == 0, print("ECPP-FAILED"); quit(1));
v = primecertisvalid(c);
print("pari_selfcheck=", v);
f = fileopen("{pf}.cert", "w");
filewrite(f, Str(c));
fileclose(f);
quit(0);
'''
    open(os.path.join(work, "gen_cert.gp"), "w").write(gp)
    print("running PARI primecert (ECPP)...", flush=True)
    r = subprocess.run(["gp", "-q", os.path.join(work, "gen_cert.gp")],
                       capture_output=True, text=True)
    print(r.stdout[-2000:], r.stderr[-500:])
    assert "pari_selfcheck=1" in r.stdout, "PARI ECPP failed"
    cert = pari_tokens_to_json(open(pf + ".cert").read())
    # independent re-verification (pure python checker)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import ecpp_verify
    ok, info = ecpp_verify.verify(cert)
    assert ok and int(info) == int(P), f"independent ECPP verify failed: {info}"
    print("independent python ECPP verify: OK")
    if not a.skip_aprcl:
        print("running PARI APR-CL as second algorithm...", flush=True)
        gp2 = os.path.join(work, "aprcl_run.gp")
        open(gp2, "w").write(f'default(parisizemax,8000000000);\n'
                             f'P = eval(readstr("{pf}")[1]);\n'
                             f'print("aprcl=", isprime(P, 2));\nquit\n')
        r2 = subprocess.run(["gp", "-q", gp2], capture_output=True, text=True, timeout=1000000)
        assert "aprcl=1" in r2.stdout, f"APR-CL disagrees! {r2.stdout[-300:]} {r2.stderr[-300:]}"
        print("APR-CL: prime")
    pkg = {"N": str(N), "q": a.q, "t": a.t,
           "classes": [[r, b] for r, b in classes],
           "ecpp_cert": cert, "claims": json.loads(a.claims),
           "cover_meta": {"Q": cov["Q"], "k": cov["k"], "spent_nats": cov["spent"]}}
    json.dump(pkg, open(a.out, "w"))
    h = hashlib.sha256(open(a.out, "rb").read()).hexdigest()
    print(f"package -> {a.out}\nsha256: {h}")

if __name__ == "__main__":
    main()
