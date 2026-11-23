\\ Direct PARI check: N - p composite for every prime p < g (ispseudoprime is BPSW; a composite verdict is definite), N - g prime (isprime proves it).
default(parisize, 256000000);
N = 50583740589138609697834580677536505029993742021564403324742841593805675019483643333405234558658003443364952736004219490803519504354430208924939648722453717301132634879292790425977206547799605815328328; g = 158209;
c = 0; forprime(p = 2, g - 1, if(ispseudoprime(N - p), error("N - p prime at p = ", p)); c++);
print("primes p < g checked: ", c, "; isprime(g) = ", isprime(g), "; isprime(N - g) = ", isprime(N - g), "; N even: ", N % 2 == 0, "; digits: ", #Str(N));
