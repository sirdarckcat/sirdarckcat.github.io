from fam import world, rows_upto, GD
p, F, R, x, el = world(3)
rows = rows_upto(R, F, el, 3, 9)
N = x**21+2*x**19+x**15+2*x**13+2*x**7+2*x**3+2*x+2
print("N(x+1)==N:", N.compose(x+1) == N, "GD:", GD(N, rows, 21), "rows deg<=8:", sum(1 for Q in rows if Q.degree() <= 8))
N = x**18+2*x**15+2*x**14+x**13+x**11+x**9+2*x**7+x**6+x**5+2*x**3+x+2
print("(3,18) optimum GD:", GD(N, rows, 18), "N' =", N.derivative(), "N(x+1)==N", N.compose(x+1)==N)
