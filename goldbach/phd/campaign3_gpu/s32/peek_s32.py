import os
r = "/content/s32g/result.txt"
print("[ps32]", open(r).read() if os.path.exists(r) else ("status: " + (open("/content/s32g/status.txt").read().strip().replace("\n", " || ") if os.path.exists("/content/s32g/status.txt") else "none")))
