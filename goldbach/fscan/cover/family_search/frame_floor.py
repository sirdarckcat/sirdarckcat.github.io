# The floor of a family of covers at warm temperatures: a cheap, low-noise score for the family.
#
#   python3 family_search/frame_floor.py ranked.txt first last [sweeps=10000] [seed=1] [weights=family_search/weights_8.9days.txt] [last_modulus=491]
#                                                                                                        (run from cover/)
# ranked.txt: the output of frame_rank.py ("rank | weighted rows alive | rows alive below Q | frame").  For the frames
# ranked first..last: the classes of the frame are held fixed (COVER_FLOOR_FRAME of ../../sublinear/cover_floor.c, built
# here as ./cover_floor_frame if it is missing), the other moduli (odd primes up to 461 and last_modulus) are tempered
# on the weighted rows at 20 temperatures up to beta = 1.31, and the floor -ln Z/beta of the family is printed at
# beta = 0.99 and 1.15, with the mean rows there in the first and the last quarter of the run (a falling mean = not
# yet in equilibrium, floor too high).  One line per frame:  rank | frame | floor(0.99) | floor(1.15) | <k>(0.99) quarters.
#
# Why this score.  At the same tempering budget (20,000 sweeps of frame_search.py) family B reaches 1,311.6 weighted
# rows, the runner-up family 1,317.8 and the two frames that leave the fewest rows alive 1,325.0 and 1,320.6; their
# floors at beta = 0.99 are 1,231.7, 1,232.3, 1,235.1 and 1,236.6 (two seeds within 1.5, 20 seconds each).  The rows a
# frame leaves alive (frame_rank.py) order the families only roughly: family B is 121st of 92,160 on that count.
import os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__)); sub = os.path.join(here, "..", "..", "..", "sublinear")
sys.path.insert(0, sub)
import cover_floor as cf
ranked, first, last = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
sweeps = sys.argv[4] if len(sys.argv) > 4 else "10000"; seed = sys.argv[5] if len(sys.argv) > 5 else "1"
wfile = sys.argv[6] if len(sys.argv) > 6 else os.path.join(here, "weights_8.9days.txt"); lastmod = int(sys.argv[7]) if len(sys.argv) > 7 else 491
exe = "./cover_floor_frame"
if not os.path.exists(exe): subprocess.run(["gcc", "-O3", "-march=native", "-fopenmp", "-o", exe, os.path.join(sub, "cover_floor.c"), "-lm"], check=True)
def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
tmp = f"/tmp/frame_floor_{os.getpid()}"
open(tmp + ".mod", "w").write(" ".join(str(p) for p in primes_upto(461) if p > 2) + f" {lastmod}\n")
open(tmp + ".betas", "w").write("0 0.02 0.05 0.09 0.14 0.2 0.27 0.35 0.43 0.51 0.59 0.67 0.75 0.83 0.91 0.99 1.07 1.15 1.23 1.31\n")
for line in open(ranked):
    t = [u.strip() for u in line.split("|")]
    if len(t) != 4 or not t[0].isdigit() or not first <= int(t[0]) <= last: continue
    env = dict(os.environ, COVER_FLOOR_FRAME=t[3], COVER_FLOOR_WEIGHTS=wfile, OMP_NUM_THREADS="1", OMP_WAIT_POLICY="passive")
    subprocess.run([exe, "170000", tmp + ".mod", tmp + ".betas", sweeps, str(int(sweeps) // 5), tmp + ".out", seed], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    par, reps = cf.analyse(tmp + ".out"); r = {round(x["beta"], 2): x for x in reps}
    print(f"{t[0]} | {t[3]} | {r[0.99]['floor']:.2f} | {r[1.15]['floor']:.2f} | {r[0.99]['quarters'][0]:.1f} {r[0.99]['quarters'][3]:.1f}", flush=True)
for e in (".mod", ".betas", ".out"):
    if os.path.exists(tmp + e): os.remove(tmp + e)
