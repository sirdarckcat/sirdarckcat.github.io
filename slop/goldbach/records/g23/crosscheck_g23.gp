{
N = eval(readstr("N_g23.txt")[1]);
q = 110917;
cnt = 0; bad = 0;
forprime(p = 2, q,
  pr = ispseudoprime(N - p);
  if (pr && p < q, print("VIOLATION at p=", p); bad++);
  if (p == q && !pr, print("q COMPLEMENT NOT PRIME"); bad++);
  cnt++);
print("scanned primes: ", cnt, "  violations: ", bad);
if (bad == 0 && cnt == 10526,
  print("CROSSCHECK PASS: g(N) = ", q),
  print("CROSSCHECK FAIL"));
}
quit
