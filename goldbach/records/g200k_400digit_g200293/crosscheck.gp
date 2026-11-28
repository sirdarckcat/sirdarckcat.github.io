\\ Direct PARI check: N even; g prime; N - p composite for every prime p < g
\\ (ispseudoprime is BPSW; a composite verdict is definite); N - g proven prime
\\ by isprime(N - g) AND complement_cert.gp validated with top-level binding.
default(parisize, 512000000);
N = 1706006024658937925971713412697419426439230400811324091081053167288470005778359661526768130651075521058300214063933906686801581941695954813875563592708868012505365249807655171892780490355507164595899237601084131108400181430631383784220855905459889013499475848556817021901913361705426666451987984503705154078439570770131964752681177369649797799434570270205182928873900699904782751252408742852732592412; g = 200293;
if(N % 2 != 0, print("FAIL: N is odd"); quit(1));
if(!isprime(g), print("FAIL: g is not prime"); quit(1));
c = 0; forprime(p = 2, g - 1, if(ispseudoprime(N - p), print("FAIL: N - p prime at p = ", p); quit(1)); c++);
p_ok = 0; p_ok = iferr(isprime(N - g), E, 0);
if(type(p_ok) != "t_INT" || p_ok != 1, print("FAIL: N - g not proven prime"); quit(1));
safe_cert(p1, p2, p3) = {
  my(raw, s, bs, ch);
  raw = iferr(readstr(p1), E1, iferr(readstr(p2), E2, iferr(readstr(p3), E3, 0)));
  if(type(raw) != "t_VEC" || #raw < 1, return(0));
  s = strjoin(raw, "\n");
  bs = Vecsmall(s);
  if(#bs < 2, return(0));
  for(i = 1, #bs, ch = bs[i]; if(!((ch >= 48 && ch <= 57) || ch == 91 || ch == 93 || ch == 44 || ch == 45 || ch == 32 || ch == 9 || ch == 10 || ch == 13), return(0)));
  iferr(eval(s), E, 0);
};
cert = 0; cert = safe_cert("complement_cert.gp", "records/g200k_400digit_g200293/complement_cert.gp", "goldbach/records/g200k_400digit_g200293/complement_cert.gp");
c_ok = 0; c_ok = iferr((type(cert) == "t_VEC") && (#cert >= 1) && (type(cert[1]) == "t_VEC") && (#cert[1] >= 1) && (type(cert[1][1]) == "t_INT") && (cert[1][1] == N - g) && (primecertisvalid(cert) == 1), E, 0);
if(type(c_ok) != "t_INT" || c_ok != 1, print("FAIL: complement_cert.gp invalid or top-level mismatch"); quit(1));
print("primes p < g checked: ", c, "; isprime(g) = ", isprime(g), "; isprime(N - g) = ", p_ok, "; primecertisvalid(cert) = ", c_ok, "; N even: ", N % 2 == 0, "; digits: ", #Str(N));
quit(0);
