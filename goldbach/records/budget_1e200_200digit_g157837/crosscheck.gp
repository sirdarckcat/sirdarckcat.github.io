\\ Direct PARI check: N - p composite for every prime p < g (ispseudoprime is BPSW; a composite verdict is definite), N - g prime (isprime proves it).
default(parisize, 256000000);
N = 77674393411106372037785741609148759532201866595844925004069305259376785028458059444586695037279120087424944926035330358836277635018594469510412190238072490182642415096768996238992699953873325601950178; g = 157837;
c = 0; forprime(p = 2, g - 1, if(ispseudoprime(N - p), error("N - p prime at p = ", p)); c++);
print("primes p < g checked: ", c, "; isprime(g) = ", isprime(g), "; isprime(N - g) = ", isprime(N - g), "; N even: ", N % 2 == 0, "; digits: ", #Str(N));
