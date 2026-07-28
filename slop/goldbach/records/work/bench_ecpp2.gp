default(parisize, 2000000000);
default(parisizemax, 8000000000);
default(threadsize, 1000000000);
default(threadsizemax, 4000000000);
setrand(43);
p2 = randomprime([10^2399, 10^2400]);
t2 = getabstime(); c2 = primecert(p2); t2 = getabstime() - t2;
printf("primecert 2400d: %.1f s, valid=%d\n", t2/1000.0, primecertisvalid(c2));
quit
