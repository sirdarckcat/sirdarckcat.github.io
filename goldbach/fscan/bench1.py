#!/usr/bin/env python3
"""CPU seconds of one executable on one progression (v4532, 191 residual primes), 2^29 members from k = 2^26.
    python3 bench1.py exe theta Ta [extra args]"""
import resource, subprocess, sys
exe, th, ta = sys.argv[1:4]
n0, M = 9687738708244276, 13082761331670030
LOG = int(__import__("os").environ.get("LOGK", "29"))
xmin, xmax = n0 + (1 << 26) * M - 1, n0 + ((1 << 26) + (1 << LOG) - 1) * M
r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
out = subprocess.run([exe, "10007", __import__("os").environ.get("LSC", "383"), "191", "191", str(xmin), str(xmax), th, ta, f"one={n0}", "threads=1"] + sys.argv[4:],
                     capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1]
cpu = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime - r0.ru_utime
st = dict(kv.split("=") for kv in out.split(" | ")[1].split())
print(f"{exe} theta={th} Ta={ta}: {cpu:.2f} CPU s, {cpu * 2.3e9 / int(st['members']):.2f} cycles/member, selected {st['selected']} kept {st['kept']} tests {st['tests']} "
      f"expected {st.get('expected')} raw {st.get('expected_raw')}")
