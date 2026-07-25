{
N = eval(readstr("N_t100k_r2.txt")[1]);
q = 109357;
cnt = 0; bad = 0;
forprime(p = 2, q,
  pr = ispseudoprime(N - p);
  if (pr && p < q, print("VIOLATION at p=", p); bad++);
  if (p == q && !pr, print("q COMPLEMENT NOT PRIME"); bad++);
  cnt++);
print("scanned primes: ", cnt, "  violations: ", bad);
}
quit
