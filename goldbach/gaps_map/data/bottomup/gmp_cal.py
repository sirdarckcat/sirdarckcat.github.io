# Calibration of the ratio between one big FFT multiplication (the unit of Bernstein's batch smooth-part algorithm)
# and one 665-bit Fermat test, on this machine, using libgmp through ctypes (no headers needed).
import ctypes, time, os, sys
g = ctypes.CDLL('libgmp.so.10')
class MPZ(ctypes.Structure): _fields_ = [('alloc', ctypes.c_int), ('size', ctypes.c_int), ('d', ctypes.c_void_p)]
P = ctypes.POINTER(MPZ)
def mk():
    z = MPZ(); g.__gmpz_init(ctypes.byref(z)); return z
def setrand(z, bits):
    nb = (bits + 7) // 8; buf = os.urandom(nb)
    g.__gmpz_import(ctypes.byref(z), ctypes.c_size_t(nb), 1, 1, 1, 0, buf)
    g.__gmpz_setbit(ctypes.byref(z), ctypes.c_ulong(bits - 1))    # full length
def fermat_time(bits=665, reps=2000):
    m = mk(); setrand(m, bits); g.__gmpz_setbit(ctypes.byref(m), 0)    # odd
    e = mk(); g.__gmpz_sub_ui(ctypes.byref(e), ctypes.byref(m), 1)
    b = mk(); g.__gmpz_set_ui(ctypes.byref(b), 2); r = mk()
    t = time.perf_counter()
    for _ in range(reps): g.__gmpz_powm(ctypes.byref(r), ctypes.byref(b), ctypes.byref(e), ctypes.byref(m))
    return (time.perf_counter() - t) / reps
def mul_time(bits, reps=1):
    a = mk(); b = mk(); r = mk(); setrand(a, bits); setrand(b, bits)
    t = time.perf_counter()
    for _ in range(reps): g.__gmpz_mul(ctypes.byref(r), ctypes.byref(a), ctypes.byref(b))
    return (time.perf_counter() - t) / reps
def div_time(zbits, mbits, reps=1):
    z = mk(); m = mk(); r = mk(); q = mk(); setrand(z, zbits); setrand(m, mbits); g.__gmpz_setbit(ctypes.byref(m), 0)
    t = time.perf_counter()
    for _ in range(reps): g.__gmpz_tdiv_r(ctypes.byref(r), ctypes.byref(z), ctypes.byref(m))
    return (time.perf_counter() - t) / reps
tf = fermat_time(); print('Fermat test base 2 (mpz_powm), 665-bit modulus: %.1f us' % (tf * 1e6))
for bits in [10**6, 10**7, 10**8, 3 * 10**8]:
    tm = mul_time(bits); print('mpz_mul of two %.1e-bit numbers: %.3f s = %.0f Fermat tests' % (bits, tm, tm / tf), flush=True)
for zb, mb in [(144 * 10**6, 10**6), (144 * 10**6, 10**7)]:
    td = div_time(zb, mb); print('mpz_tdiv_r of a %.2e-bit number by a %.0e-bit one: %.3f s = %.0f Fermat tests' % (zb, mb, td, td / tf), flush=True)
