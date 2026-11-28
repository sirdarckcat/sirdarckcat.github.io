\\ Independent PARI/GP cross-check (separate code path from verify.py).
\\   gp -q crosscheck.gp
\\ 1. P = N - g is prime: PARI's own N-1 (Pocklington-Lehmer) certificate,
\\    built and validated by PARI, plus PARI's default isprime().
\\ 2. Brute-force scan, not using the cover classes at all: for EVERY prime
\\    q < g, N - q shares a factor with the primorial of the largest cover
\\    modulus (and is far larger than it), hence is composite.  The scan is
\\    a parforprime over all threads (it runs sequentially on a PARI built
\\    without threads); cnt checks that every prime q < g was visited.
\\ Fail-stop: gp carries on with the next line after an error, so every check
\\ sets a flag on its own line and die() quits with exit status 1 unless the
\\ flag is set; a PASSED line can only follow passing checks.
\\ Split runs, for big records: put e.g. "qlo = 2; qhi = 4000000;" in range.gp and
\\ run  gp -q range.gp crosscheck.gp  to scan only the primes in [qlo, qhi).
\\ A split run skips step 1 (add "cert = 1;" to keep it) and prints RANGE PASSED;
\\ the ranges' counts must add up to primepi(g - 1).
default(parisize, 2000000000);
die(s) = print("CROSSCHECK FAILED: ", s); quit(1);
ok = 0; N = eval(readstr("N.txt")[1]); ok = type(N) == "t_INT";
if (!ok, die("N.txt unreadable"));
g = 16046137; rmax = 459089;
P = N - g;
full = type(qlo) == "t_POL" && type(qhi) == "t_POL";
if (type(qlo) == "t_POL", qlo = 2);
if (type(qhi) == "t_POL", qhi = g);
if (type(cert) == "t_POL", cert = full);
if (type(qlo) != "t_INT" || type(qhi) != "t_INT" || qlo < 2 || qhi > g || qlo >= qhi, die("need integers 2 <= qlo < qhi <= g"));
ok = 0; ok = isprime(g);
if (!ok, die("g not prime"));
ok = !cert; if (cert, c = primecert(P, 1); ok = c != 0);
if (!ok, die("no N-1 certificate: P not prime?"));
ok = !cert; if (cert, ok = primecertisvalid(c));
if (!ok, die("PARI rejects its N-1 certificate"));
if (cert, print("PARI N-1 (Pocklington-Lehmer) certificate for P = N - g: valid"));
ok = !cert; if (cert, ok = isprime(P));
if (!ok, die("isprime(P) = 0"));
if (cert, print("PARI isprime(P) = 1"));
ok = 0; PR = vecprod(primes([2, rmax])); ok = 1;
if (!ok, die("primorial failed"));
done = 0; cnt = 0; bad = 0; export(N, PR); parforprime(q = qlo, qhi - 1, gcd(N - q, PR) == 1, isbad, cnt++; if (isbad, bad++)); done = 1;
want = primepi(qhi - 1) - primepi(qlo - 1);
if (full, print("primes q < g scanned: ", cnt, "   (pi(g-1) = ", primepi(g - 1), ")"));
if (!full, print("primes q in [", qlo, ", ", qhi, ") scanned: ", cnt, "   (primepi difference = ", want, ")"));
print("complements N - q with no prime factor <= ", rmax, ": ", bad);
if (!done || bad != 0 || cnt != want, die("SCAN FAILED"));
ok = 0; ok = gcd(P, PR) == 1;
if (!ok, die("P has a small factor"));
if (full, print("CROSSCHECK PASSED: g(N) = ", g));
if (!full, print("RANGE PASSED: [", qlo, ", ", qhi, "), ", cnt, " primes, g = ", g));
