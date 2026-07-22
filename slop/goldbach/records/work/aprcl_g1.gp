default(parisize, 2000000000);
default(parisizemax, 8000000000);
default(threadsize, 1000000000);
default(threadsizemax, 4000000000);
P = eval(readstr("P_1157341.txt")[1]);
gettime();
print("aprcl=", isprime(P, 2), " ms=", gettime());
quit
