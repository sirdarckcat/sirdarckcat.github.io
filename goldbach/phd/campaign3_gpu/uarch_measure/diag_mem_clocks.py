import os
print("[mem]", os.popen("nvidia-smi --query-gpu=name,memory.used,memory.total,clocks.sm,clocks.max.sm,power.draw,power.limit,clocks_throttle_reasons.active,ecc.mode.current --format=csv,noheader").read().strip(),
      "| procs:", os.popen("nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader").read().strip().replace("\n", " ; "))
