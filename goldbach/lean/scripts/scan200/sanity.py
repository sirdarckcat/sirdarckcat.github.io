"""End-to-end sanity check of the pipeline on one cover: the C sieve against trial division, and the C member loop
(fm13) against gmpy2, on the emptiest members of one window.   python sanity.py CODE_DIR SPEC.json"""
import json, sys, time
import numpy as np, gmpy2
code, specf = sys.argv[1], sys.argv[2]
sys.path.insert(0, code + "/goldbach/sieve200"); sys.path.insert(0, code + "/goldbach/fermat661")
import sieve200, fm13
spec = json.load(open(specf))[0]; N0, M, U = int(spec["N0"]), int(spec["M"]), [int(q) for q in spec["residual"]]
cover = [r for r, _ in spec["cover"]]
assert N0 % 2 == 0 and all(N0 % r == a for r, a in spec["cover"]) and M == 2 * np.prod([int(r) for r in cover], dtype=object)
B = 200000; sv = sieve200.Sieve200(N0, M, U, B, logK=15, exclude=cover)
k0 = 5 * 32768; t = time.time(); cnt, bits = sv.block(k0); print(f"sieve of 32,768 members to {B}: {time.time() - t:.2f} s; alive rows per member {cnt.mean():.1f} of {len(U)}")
order = np.argsort(cnt, kind="stable")[:96]
rows, offs = sv.survivors(bits, order.astype(np.uint32)); rows = rows.tolist(); offs = offs.tolist()
# sieve against trial division on 6 members
p = 3; ps = []
while p < B:
    if M % p: ps.append(p)
    p = int(gmpy2.next_prime(p))
bad = 0
for t_ in range(6):
    N = N0 + (k0 + int(order[t_])) * M
    want = [i for i, q in enumerate(U) if all((N - q) % s for s in ps)]
    bad += want != rows[offs[t_]:offs[t_ + 1]]
print("members whose alive rows differ from trial division:", bad, "of 6")
fm = fm13.Members(N0, M, U); t = time.time()
fp = fm.first_pass(order.astype(np.uint64) + k0, np.array(rows, dtype=np.uint16), np.array(offs, dtype=np.int64)).tolist(); dt = time.time() - t
wrong = tests = 0
for t_ in range(len(order)):
    N = N0 + (k0 + int(order[t_])) * M; pos = -1
    for j, i in enumerate(rows[offs[t_]:offs[t_ + 1]]):
        n = N - U[i]; tests += 1
        if gmpy2.powmod(2, n - 1, n) == 1: pos = j; break
    wrong += pos != fp[t_]
print(f"first probable prime of each of {len(order)} members, fm13 against gmpy2: {wrong} differ; {tests} tests, {dt / tests * 1e6:.1f} microseconds a test in fm13")
print("number of digits of the largest member:", len(str(N0 + (spec['kmax'] - 1) * M)), "| bits:", (N0 + spec['kmax'] * M).bit_length())
