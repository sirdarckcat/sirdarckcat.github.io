\\ Direct PARI check: N - p composite for every prime p < g (ispseudoprime is BPSW; a composite verdict is definite), N - g prime (isprime proves it).
default(parisize, 256000000);
N = 95347106818046249718570776328527805394387907539756369117325081343361548773031798520383947495686099037769506167416423881905531645343709972339865033333397602306957446186830655985687114607924513408740178; g = 160357;
c = 0; forprime(p = 2, g - 1, if(ispseudoprime(N - p), error("N - p prime at p = ", p)); c++);
print("primes p < g checked: ", c, "; isprime(g) = ", isprime(g), "; isprime(N - g) = ", isprime(N - g), "; N even: ", N % 2 == 0, "; digits: ", #Str(N));
