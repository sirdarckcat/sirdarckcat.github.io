chk(N, g) = {
  my(bad = 0, cnt = 0);
  if (N % 2, error("N odd"));
  if (!isprime(g) || !isprime(N - g), error("g or N - g not prime"));
  forprime(q = 2, g - 1, cnt++; if (ispseudoprime(N - q), bad++));
  if (bad, error("a smaller prime works"));
  print("PROVED g(N) = ", g, " for N = ", N, " (", #Str(N), " digits; ", cnt, " smaller primes all give composite N - q)");
}
chk(54284735534856910692542, 11701);
quit
