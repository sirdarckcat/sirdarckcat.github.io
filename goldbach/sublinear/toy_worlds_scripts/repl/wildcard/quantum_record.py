#!/usr/bin/env python3
"""For the record only (no quantum computer is available): what Grover search and its relatives give on this problem.
All figures are a model: the campaign's hit chance per member, Toffoli counts scaled from published modular-exponentiation
circuits (about 0.2 n^3 Toffolis for an n-bit modulus and an n-bit exponent with windowed arithmetic: FROM MEMORY of
Gidney and Ekera's 0.3 n^3 for an exponent of 1.5 n bits)."""
import sys, math
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
rows, p = cr.load(cr.S + "q200000_m89.txt"); rows = rows[rows < 200000]
lam = -math.log(1 - p); E = lam * len(rows)
print(f"rows {len(rows)}, chance a row is prime {p:.5f}, exponent at 200,000: {E:.2f} nats (a member is a hit with chance e^-{E:.2f})")
lnK = math.log(21378977)
print(f"one window: e^{lnK:.2f} members, expected hits e^{lnK - E:.2f}; windows needed classically e^{E - lnK:.2f} = {math.exp(E - lnK):.3g}")
it = math.pi / 4 * math.exp(E / 2)
print(f"Grover over the union of those windows: (pi/4) e^(E/2) = {it:.3g} coherent iterations ({math.log(it):.2f} nats); optimal for a black-box predicate (BBBV 1997, Zalka 1999)")
n = 664; tof_fermat = 0.2 * n ** 3
print(f"one coherent Fermat test of a {n}-bit number: about {tof_fermat:.2g} Toffoli gates")
full = 2 * len(rows) * tof_fermat
print(f"oracle with every row tested (compute and uncompute): {full:.2g} Toffolis; total {it * full:.2g} Toffolis in sequence")
# variable-time search (Ambainis 2010): cost ~ sqrt(sum over members of t^2), t = tests until the first prime among the rows
q = p; m = len(rows)
Et2 = sum((j + 1) ** 2 * (1 - q) ** j * q for j in range(m)) + m * m * (1 - q) ** m
print(f"variable-time search: root-mean-square number of rows tested per member {math.sqrt(Et2):.1f} (of {m}); total about {it * 2 * math.sqrt(Et2) * tof_fermat:.2g} Toffolis, before its logarithmic overhead")
for rate, nm in ((1e6, "10^6 Toffolis a second"), (1e9, "10^9 a second")):
    print(f"   at {nm}: {it * 2 * math.sqrt(Et2) * tof_fermat / rate / 3.15e7:.3g} years (Grover does not parallelise: P machines gain sqrt(P))")
print(f"classical work available is e^31 member-equivalents; the same exponent 31 would let a quantum search reach an exponent of 62 nats in iterations, i.e. the level where the classical exponent is 62")
# the arc: meet in the middle e^(D/2) classically; quantum collision finding e^(D/3) (Brassard-Hoyer-Tapp, with e^(D/3) quantum memory)
for D, what in ((26.5, "seven later primes"), (496, "the primes to 1,000"), (1479, "the primes to 2,000")):
    print(f"arc of precision D = {D} ({what}): classical lists e^{D / 2:.0f}, quantum collision search e^{D / 3:.0f}")
