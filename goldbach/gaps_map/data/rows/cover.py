import numpy as np, math, time
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
Q = 200000
P = primes_upto(Q - 1); rows_all = P[P > 2]; print('odd primes below Q:', len(rows_all))
mods = [int(p) for p in primes_upto(463) if p > 2]; print('moduli', len(mods), mods[0], mods[-1])
theta = sum(math.log(p) for p in mods) + math.log(2)
print('ln(2*prod odd primes <=463) = %.2f = 10^%.2f ; ln(1e200) = %.2f' % (theta, theta / math.log(10), 200 * math.log(10)))
def greedy(mods, rows):
    cnt = np.zeros(len(rows), dtype=np.int32); cls = {}
    for p in mods:
        alive = cnt == 0; b = np.bincount(rows[alive] % p, minlength=p); c = int(b.argmax()); cls[p] = c; cnt[(rows % p) == c] += 1
    return cls, cnt
def coord_descent(mods, rows, cls, cnt, passes=30):
    for ps in range(passes):
        improved = 0
        for p in mods:
            c0 = cls[p]; cnt[(rows % p) == c0] -= 1
            alive = cnt == 0; b = np.bincount(rows[alive] % p, minlength=p); c = int(b.argmax())
            if b[c] > b[c0]: improved += b[c] - b[c0]
            cls[p] = c; cnt[(rows % p) == c] += 1
        if improved == 0: break
    return cls, cnt, ps
t0 = time.time(); cls, cnt = greedy(mods, rows_all); print('greedy alive rows', int((cnt == 0).sum()), round(time.time() - t0, 1), 's')
cls, cnt, ps = coord_descent(mods, rows_all, cls, cnt); print('after coordinate descent (%d passes) alive rows' % (ps + 1), int((cnt == 0).sum()))
np.save('rows_alive.npy', rows_all[cnt == 0]); np.save('cls.npy', np.array([cls[p] for p in mods]))
