# Test vectors for the fermat28 kernel (compiled for the CPU) and for the Lean model Gpu28.
# Writes tests.txt and expected.txt (big-integer arithmetic) in the current directory.
import random
random.seed(20261122)
L = 24; B = 1 << 28; R = 1 << 672
tests = []; exp = []
def step(n, X, b):
    assert n % 2 == 1 and 0 <= X < 4 * n and 16 * n < R
    m = (-X * X * pow(n, -1, R)) % R                 # the Montgomery quotient
    Y = ((X * X + m * n) >> 672) << b
    assert (X * X + m * n) % R == 0 and Y < 4 * n
    tests.append("step %x %x %d" % (X, n, b)); exp.append("step %0168x" % Y)
for trial in range(240):
    bits = random.choice([642, 650, 660, 664, 665, 667, 668, 668, 668])
    n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
    kind = trial % 6
    if kind == 0: X = random.randrange(0, 4 * n)
    elif kind == 1: X = 4 * n - 1 - random.randrange(0, 1000)
    elif kind == 2: X = min(4 * n - 1, (1 << 670) - 1)
    elif kind == 3: X = random.randrange(0, 1 << 40)
    elif kind == 4: X = (random.getrandbits(24 * 28) | sum((B - 1) << (28 * i) for i in range(0, 24, 2))) % (4 * n)
    else: X = random.randrange(n, 4 * n)
    step(n, X, random.randrange(2))
for n in ((1 << 668) - 1, (1 << 668) - 3, (1 << 667) | 1, (1 << 641) | 1, (1 << 668) - (1 << 40) - 1):
    for X in (4 * n - 1, 4 * n - 2, 2 * n, n, 1, 0):
        for b in (0, 1): step(n, X, b)
for lo in [1, 3, 5, 7, 0xffffffff, 0xfffffffd, 0x10000001, 0x0fffffff, 0x80000001] + [random.getrandbits(32) | 1 for _ in range(60)]:
    tests.append("inv %x" % lo); exp.append("inv %07x" % ((-pow(lo, -1, B)) % B))
def is_prp(n): return pow(2, n - 1, n) == 1
def fermat(n):
    bn = n.bit_length()
    f = 2 if (bn < 642 or bn > 668 or n % 2 == 0) else int(is_prp(n))
    tests.append("fermat %x" % n); exp.append("fermat %d" % f)
for bits in (642, 650, 665, 668):
    fermat(random.getrandbits(bits) | (1 << (bits - 1)) | 1)          # composite with overwhelming probability
    n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
    while not is_prp(n): n += 2
    if n.bit_length() == bits: fermat(n)                              # a probable prime
fermat((1 << 641) + 1); fermat((1 << 668) - 1); fermat((1 << 668) - 3)
fermat((1 << 641) - 1); fermat((1 << 668) + 1); fermat((1 << 660) + 2)  # out of range or even: flag 2
open("tests.txt", "w").write("\n".join(tests) + "\n"); open("expected.txt", "w").write("\n".join(exp) + "\n")
print(len(tests), "tests")
