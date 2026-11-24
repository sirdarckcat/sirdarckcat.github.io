"""check desert_fast / desert_fast2 output lines: the vector's least unstruck odd prime equals the printed D, and D equals the published value (n <= 15)"""
import sys, re
KNOWN = {1: 5, 2: 7, 3: 19, 4: 31, 5: 43, 6: 67, 7: 103, 8: 163, 9: 181, 10: 223, 11: 271, 12: 331, 13: 419, 14: 499, 15: 613}
def primes(lim):
    s = bytearray([1]) * lim; s[0] = s[1] = 0
    for i in range(2, int(lim ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(3, lim) if s[i]]
P = primes(20000)
ok = True
for line in sys.stdin:
    m = re.search(r"n=(\d+) .*D=(\d+).*vector:(.*)", line)
    if not m: continue
    n, D = int(m.group(1)), int(m.group(2))
    vec = [tuple(map(int, t.split(":"))) for t in m.group(3).split()]
    q = next(p for p in P if all(p % r != c for r, c in vec))
    good = q == D and KNOWN.get(n, D) == D and len(vec) == n
    print(f"  n={n}: D={D} (published {KNOWN.get(n, '?')}), the vector's least unstruck prime {q}: {'ok' if good else 'WRONG'}")
    ok &= good
print("CHECK OK" if ok else "CHECK FAILED")
