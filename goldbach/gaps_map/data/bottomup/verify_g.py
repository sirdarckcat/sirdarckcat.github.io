# Independent check of every find of the calibration scan from its N alone: g(N) = least prime p with N - p prime.
# Compositeness of N - p for p < g is certified (a small factor or a failed Fermat base-2 test: rigorous); N - g is checked by Miller-Rabin to 12 bases (probable prime).
import sys, json, glob, time
files = sorted(glob.glob(sys.argv[1] + '/f479t80000_found_w3*.jsonl'))
ev = []
for f in files:
    ev += [json.loads(l) for l in open(f) if l.strip()]
lim = 140000
sv = bytearray([1]) * (lim + 1); sv[0] = sv[1] = 0
for i in range(2, int(lim ** .5) + 1):
    if sv[i]: sv[i * i::i] = bytearray(len(sv[i * i::i]))
P = [i for i in range(2, lim + 1) if sv[i]]
small = [p for p in P if p < 400]
def mr(n, bases=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)):
    if n < 4: return n in (2, 3)
    d = n - 1; s = 0
    while d % 2 == 0: d //= 2; s += 1
    for a in bases:
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True
t0 = time.time(); bad = 0; tests = 0
for e in ev:
    N = int(e['N']); g = int(e['g']); first = None
    for p in P:
        M = N - p
        if M <= 1: break
        if any(M % q == 0 for q in small): continue
        tests += 1
        if pow(2, M - 1, M) != 1: continue          # composite, certified
        if mr(M): first = p; break
    flag = 'ok' if first == g else 'MISMATCH'
    bad += first != g
    print(e['name'], 'digits', len(str(N)), 'reported g', g, 'recomputed', first, flag, flush=True)
print('checked', len(ev), 'finds, mismatches', bad, ', %d Fermat tests, %.0f s' % (tests, time.time() - t0))
