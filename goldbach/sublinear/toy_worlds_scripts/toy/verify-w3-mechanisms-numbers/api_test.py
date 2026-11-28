import flint, time
from flint import fq_default_ctx, fq_default_poly_ctx
for k in (1,2,4):
    F = fq_default_ctx(2, k, var='z')
    R = fq_default_poly_ctx(F)
    x = R.gen()
    z = F.gen()
    print(k, F, z, F.order(), type(z))
    f = x**5 + z*x + 1
    print(f, f.degree(), f.coeffs(), f.derivative(), f.factor(), f.is_irreducible(), f.is_squarefree())
    c = z+1
    print(c**3, c.trace() if hasattr(c,'trace') else None, [m for m in dir(c) if not m.startswith('_')])
    print([m for m in dir(f) if not m.startswith('_')])
    print(R([1,z,0,1]), F(3), )
    try: print(F([1,1]))
    except Exception as e: print('list fail', e)
    t=time.time(); g = x**256 + x**4 + x**3+z*x+1; 
    for i in range(20): g.factor()
    print((time.time()-t)/20)
