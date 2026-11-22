\\ Direct PARI check: N - p composite for every prime p < g (ispseudoprime is BPSW; a composite verdict is definite), N - g prime (isprime proves it).
default(parisize, 256000000);
N = 9806519255397062824472765467682451908097625481983877655666179056517874786554091701751807381313324813623198086928774990835290463710654433767962651104495228698940988749379805213193593709075933115577482; g = 125269;
c = 0; forprime(p = 2, g - 1, if(ispseudoprime(N - p), error("N - p prime at p = ", p)); c++);
print("primes p < g checked: ", c, "; isprime(g) = ", isprime(g), "; isprime(N - g) = ", isprime(N - g), "; N even: ", N % 2 == 0, "; digits: ", #Str(N));
