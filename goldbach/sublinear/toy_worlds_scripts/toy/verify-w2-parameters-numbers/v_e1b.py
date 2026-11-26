import math, random, numpy as np
from vcore import *
rng=random.Random(31337)
q,n=13,4; places=irreducibles(q,1)[:8]; R=residues(q,n,places)
c=[len(consistent(q,n,places,rand_lists(rng,q,places,[6]*8),R)) for _ in range(4000)]
c=np.array(c,float); print("q=13 8 points l=6 n=4, 4000 trials: mean %.3f +- %.3f (E=58.808), var %.2f (exact 31.342)"%(c.mean(),c.std(ddof=1)/math.sqrt(len(c)),c.var(ddof=1)))
