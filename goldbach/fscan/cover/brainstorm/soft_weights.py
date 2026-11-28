# Row weights for ptcover_w and for covergen's weighted mode (COVERGEN_WEIGHTS): what one more uncovered row at q
# costs the campaign, as a fraction of a row below the record in hand, times 64.
#
#   python3 brainstorm/soft_weights.py days rate record_in_hand Q reference_covers.txt > weights.txt     (run from cover/)
#
# Model of portfolio_budget.py and rank_covers.py: on a cover, the expected number of members with g >= x is
# m(x) = n * RATIO * (1 - p)^U(x), U(x) = its uncovered primes below x, and the expected final record is
# record + int (1 - e^-m(x)) dx.  One more uncovered row at q multiplies m(x) by (1 - p) for every x > q, so it costs
# -ln(1 - p) * int_{x > q} m e^-m dx.  Relative to a row below the record:
#     w(q) = int_{x > q} m e^-m dx / int_{x > record} m e^-m dx,
# which is 1 below the record, falls slowly at first (just above the record m is large: some member will pass there
# anyway) and reaches 0 where no member is expected to arrive.  m(x) is taken from the first cover of the reference
# file (the weights hardly depend on which good cover it is).  Rows whose weight rounds to 0 are left out.
import math, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from rank_covers import Model, read_covers
days, rate, hand, Q, ref = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
M = Model(days, rate, hand, Q)
cover = next(read_covers(ref))
w = M.weights(cover)
for q, x in zip(M.P.tolist(), w.tolist()):
    wi = round(64 * x)
    if wi > 0: print(q, wi)
