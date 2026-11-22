chk(N, g) = {
  my(bad = 0, cnt = 0);
  if (N % 2, error("N odd"));
  if (!isprime(g) || !isprime(N - g), error("g or N - g not prime"));
  forprime(q = 2, g - 1, cnt++; if (ispseudoprime(N - q), bad++));
  if (bad, error("a smaller prime works"));
  print("PROVED g(N) = ", g, " for N = ", N, " (", #Str(N), " digits; ", cnt, " smaller primes all give composite N - q)");
}
chk(35505990484772441527442, 10771);
quit
