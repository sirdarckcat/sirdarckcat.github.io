"""The limb geometry a generated step file declares (gen_fermat28.py: `#define FM_W / FM_NL / FM_NMAX` for a limb width other than 28; the 28-bit step files declare nothing, the defaults of fermat28_kernel.cuh)."""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))


def geometry(step_file):
    """(W, NL, NMAX): bits a limb, limbs, and n below 2^NMAX (16 n < R = 2^(W NL))"""
    text = open(os.path.join(HERE, step_file)).read()
    m = {k: re.search(r"#define %s (\d+)" % k, text) for k in ("FM_W", "FM_NL", "FM_NMAX")}
    if not any(m.values()):
        return 28, 24, 668
    assert all(m.values()), f"{step_file}: incomplete geometry"
    return tuple(int(m[k].group(1)) for k in ("FM_W", "FM_NL", "FM_NMAX"))


def rbits(step_file):
    """log2 R of the step: FM_RB if the step file declares it (a wide top digit), else FM_W * FM_NL"""
    text = open(os.path.join(HERE, step_file)).read()
    m = re.search(r"#define FM_RB (\d+)", text)
    if m:
        return int(m.group(1))
    W, NL, _ = geometry(step_file)
    return W * NL
