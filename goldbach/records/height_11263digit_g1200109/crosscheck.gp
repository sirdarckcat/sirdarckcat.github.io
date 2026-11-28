\\ Independent PARI/GP cross-check (separate code path from verify.py).
\\   gp -q crosscheck.gp
\\ 1. P = N - g is prime: PARI's own N-1 (Pocklington-Lehmer) certificate,
\\    built and validated by PARI, plus PARI's default isprime().
\\ 2. Brute-force scan, not using the cover classes at all: for EVERY prime
\\    q < g, N - q shares a factor with the primorial of the largest cover
\\    modulus (and is far larger than it), hence is composite.
default(parisize, 2000000000);
N = eval(readstr("N.txt")[1]);
g = 1200109; rmax = 17431;
P = N - g;
if (!isprime(g), error("g not prime"));
c = primecert(P, 1);
if (c == 0, error("no N-1 certificate: P not prime?"));
if (!primecertisvalid(c), error("PARI rejects its N-1 certificate"));
print("PARI N-1 (Pocklington-Lehmer) certificate for P = N - g: valid");
if (!isprime(P), error("isprime(P) = 0"));
print("PARI isprime(P) = 1");
PR = vecprod(primes([2, rmax]));
cnt = 0; bad = 0;
forprime(q = 2, g - 1, cnt++; if (gcd(N - q, PR) == 1, bad++));
print("primes q < g scanned: ", cnt, "   (pi(g-1) = ", primepi(g - 1), ")");
print("complements N - q with no prime factor <= ", rmax, ": ", bad);
if (bad > 0 || cnt != primepi(g - 1), error("SCAN FAILED"));
if (gcd(P, PR) != 1, error("P has a small factor"));
print("CROSSCHECK PASSED: g(N) = ", g);
