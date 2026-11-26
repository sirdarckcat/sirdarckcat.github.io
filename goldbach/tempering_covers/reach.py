# Independent check of a cover: the first odd prime in no class (r:a pairs), by direct trial over the primes.
#   python3 reach.py "3:2 5:3 ..."   or   python3 reach.py file   (uses the BEST / COVER / r:a line)
import sys, math
def odd_primes_below(n):
    s = bytearray([1]) * n; s[0:2] = b"\x00\x00"
    for i in range(2, math.isqrt(n - 1) + 1):
        if s[i]: s[i * i::i] = bytearray(len(range(i * i, n, i)))
    return [p for p in range(3, n, 2) if s[p]]
def parse(text):
    for line in text.splitlines():
        toks = [t for t in line.split() if ":" in t and t.split(":")[0].isdigit()]
        if len(toks) > 1: return [(int(a), int(b)) for a, b in (t.split(":") for t in toks)]
    raise SystemExit("no r:a list found")
def first_unstruck(pairs, limit=None):
    rs = [r for r, _ in pairs]; assert all(1 <= a < r for r, a in pairs), "classes must be nonzero"
    limit = limit or 4 * max(rs) * int(math.log(max(rs)) ** 2 + 10)
    for q in odd_primes_below(limit):
        if not any(q % r == a for r, a in pairs): return q
    return None
if __name__ == "__main__":
    arg = sys.argv[1]
    text = open(arg).read() if not ":" in arg else arg
    pairs = parse(text)
    print(len(pairs), "moduli, largest", max(r for r, _ in pairs), "; first odd prime in no class:", first_unstruck(pairs))
