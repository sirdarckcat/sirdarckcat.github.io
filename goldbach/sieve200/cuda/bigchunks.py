"""Chunks of primes for the staged large-prime kernel (gbig_gen_st): numpy only (the CPU tests use it without cupy)."""
import numpy as np


def make_chunks(S, ks_log, target_marks):
    """int32 [nchunks + 1]: chunk c is the primes S[ps[c]:ps[c + 1]] (S ascending).  A prime s makes about 2^ks_log / s marks a row, so the chunks are cut where the running sum of
    2^ks_log / s passes a multiple of target_marks: every chunk has about target_marks expected marks a row (a few more or less: the last prime of a chunk may carry a whole
    mark count of its own, up to 2^ks_log / s_min), and at least one prime."""
    S = np.asarray(S, dtype=np.float64)
    assert S.size > 0 and target_marks > 0
    cum = np.cumsum((1 << ks_log) / S)
    nch = max(1, int(np.ceil(cum[-1] / target_marks)))
    edges = np.searchsorted(cum, np.arange(1, nch) * target_marks, side="left") + 1
    ps = np.unique(np.concatenate([[0], np.minimum(edges, S.size), [S.size]])).astype(np.int32)
    return ps
