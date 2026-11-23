# Test vectors for the fermat28 kernel (compiled for the CPU) and for the Lean model Gpu28.
# Writes tests.txt, expected_plain.txt (steps that end with the carry chain) and expected_red.txt
# (redundant steps, x_i = y_i << b) in the current directory, from big-integer arithmetic.
import random
random.seed(20261123)
L = 24; B = 1 << 28; R = 1 << 672; M28 = B - 1
tests = []; plain = []; red = []
def words(limbs): return "".join("%08x" % v for v in reversed(limbs))
def digits(v): return [(v >> (28 * i)) & M28 for i in range(L - 1)] + [v >> (28 * (L - 1))]
def outputs(n, X, b):
    m = (-X * X * pow(n, -1, R)) % R                 # the Montgomery quotient
    assert (X * X + m * n) % R == 0
    Y = (X * X + m * n) >> 672                       # the value before the shift, below 2n
    assert Y < 2 * n and 2 * n < R >> 3
    y = digits(Y)
    assert all(v < B for v in y)
    return digits(Y << b), [v << b for v in y]
def step(n, X, b):
    assert n % 2 == 1 and 0 <= X < 4 * n and 16 * n < R
    p, r = outputs(n, X, b)
    tests.append("step %x %x %d" % (X, n, b)); plain.append("step " + words(p)); red.append("step " + words(r))
def rstep(n, xl, b):
    X = sum(v << (28 * i) for i, v in enumerate(xl))
    assert n % 2 == 1 and X < 4 * n and 16 * n < R and all(0 <= v < 2 * B for v in xl)
    p, r = outputs(n, X, b)
    tests.append("rstep %s %x %d" % (words(xl), n, b)); plain.append("rstep " + words(p)); red.append("rstep " + words(r))
def rand_n():
    bits = random.choice([642, 650, 660, 664, 665, 667, 668, 668, 668])
    return random.getrandbits(bits) | (1 << (bits - 1)) | 1
for trial in range(240):
    n = rand_n(); kind = trial % 6
    if kind == 0: X = random.randrange(0, 4 * n)
    elif kind == 1: X = 4 * n - 1 - random.randrange(0, 1000)
    elif kind == 2: X = min(4 * n - 1, (1 << 670) - 1)
    elif kind == 3: X = random.randrange(0, 1 << 40)
    elif kind == 4: X = (random.getrandbits(24 * 28) | sum(M28 << (28 * i) for i in range(0, 24, 2))) % (4 * n)
    else: X = random.randrange(n, 4 * n)
    step(n, X, random.randrange(2))
for n in ((1 << 668) - 1, (1 << 668) - 3, (1 << 667) | 1, (1 << 641) | 1, (1 << 668) - (1 << 40) - 1):
    for X in (4 * n - 1, 4 * n - 2, 2 * n, n, 1, 0):
        for b in (0, 1): step(n, X, b)
# redundant inputs: carries left in the limbs, limbs up to 2^29 - 1
for trial in range(240):
    n = rand_n(); X = random.randrange(n, 4 * n) if trial % 2 else 4 * n - 1 - random.randrange(0, 1000)
    xl = digits(X)
    for i in range(L - 1):
        if xl[i + 1] > 0 and (trial % 3 == 0 or random.random() < 0.6): xl[i] += B; xl[i + 1] -= 1
    rstep(n, xl, random.randrange(2))
for n in ((1 << 668) - 1, (1 << 668) - 3, (1 << 667) | 1, (1 << 641) | 1, rand_n(), rand_n()):
    low = [2 * B - 1] * (L - 1)                      # limbs 0 .. 22 at the maximum
    rest = 4 * n - 1 - sum(v << (28 * i) for i, v in enumerate(low))
    if rest >= 0:
        top = min(rest >> (28 * (L - 1)), 2 * B - 1)
        for b in (0, 1): rstep(n, low + [top], b)
    for b in (0, 1): rstep(n, [0] * L, b)
for lo in [1, 3, 5, 7, 0xffffffff, 0xfffffffd, 0x10000001, 0x0fffffff, 0x80000001] + [random.getrandbits(32) | 1 for _ in range(60)]:
    tests.append("inv %x" % lo); line = "inv %07x" % ((-pow(lo, -1, B)) % B); plain.append(line); red.append(line)
def is_prp(n): return pow(2, n - 1, n) == 1
def fermat(n):
    bn = n.bit_length()
    f = 2 if (bn < 642 or bn > 668 or n % 2 == 0) else int(is_prp(n))
    tests.append("fermat %x" % n); plain.append("fermat %d" % f); red.append("fermat %d" % f)
for bits in (642, 650, 665, 668):
    fermat(random.getrandbits(bits) | (1 << (bits - 1)) | 1)          # composite with overwhelming probability
    n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
    while not is_prp(n): n += 2
    if n.bit_length() == bits: fermat(n)                              # a probable prime
fermat((1 << 641) + 1); fermat((1 << 668) - 1); fermat((1 << 668) - 3)
fermat((1 << 641) - 1); fermat((1 << 668) + 1); fermat((1 << 660) + 2)  # out of range or even: flag 2
open("tests.txt", "w").write("\n".join(tests) + "\n")
open("expected_plain.txt", "w").write("\n".join(plain) + "\n"); open("expected_red.txt", "w").write("\n".join(red) + "\n")
print(len(tests), "tests")
