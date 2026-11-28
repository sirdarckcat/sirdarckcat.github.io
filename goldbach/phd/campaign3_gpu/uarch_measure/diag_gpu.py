import os, subprocess, statistics as stt
print("[dg]", os.popen("nvidia-smi --query-gpu=name,driver_version,ecc.mode.current,ecc.mode.pending --format=csv,noheader").read().strip())
print("[dg] ECC block:", " | ".join(l.strip() for l in os.popen("nvidia-smi -q -d ECC").read().splitlines() if l.strip() and ("Mode" in l or "Current" in l or "Pending" in l))[:400])
q = "clocks.sm,clocks.max.sm,clocks.mem,power.draw,power.limit,temperature.gpu,utilization.gpu,clocks_throttle_reasons.active,clocks_throttle_reasons.sw_power_cap,clocks_throttle_reasons.hw_slowdown,clocks_throttle_reasons.sw_thermal_slowdown"
out = subprocess.run(f"timeout 60 nvidia-smi --query-gpu={q} --format=csv,noheader,nounits -l 1", shell=True, capture_output=True, text=True).stdout.strip().splitlines()
rows = [[x.strip() for x in l.split(",")] for l in out if l.count(",") >= 10]
sm = [float(r[0]) for r in rows]; pw = [float(r[3]) for r in rows]
print(f"[dg] {len(rows)} samples under production | SM clock min {min(sm):.0f} median {stt.median(sm):.0f} max {max(sm):.0f} MHz (max {rows[0][1]}) | mem clock {rows[0][2]} MHz | power median {stt.median(pw):.0f} W max {max(pw):.0f} of {rows[0][4]} W limit | temp {rows[-1][5]} C | util median {stt.median(float(r[6]) for r in rows):.0f}%")
from collections import Counter
print("[dg] throttle reasons (active mask):", dict(Counter(r[7] for r in rows)), "| sw power cap:", dict(Counter(r[8] for r in rows)), "| hw slowdown:", dict(Counter(r[9] for r in rows)), "| sw thermal:", dict(Counter(r[10] for r in rows)))
