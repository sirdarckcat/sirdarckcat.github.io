P = eval(readstr("P_110917.txt")[1]);
print("P digits: ", #Str(P));
gettime();
r = isprime(P, 2);
print("aprcl=", r, " ms=", gettime());
quit
