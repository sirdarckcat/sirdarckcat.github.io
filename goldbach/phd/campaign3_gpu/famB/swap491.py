import os, shutil
S = "/content/cover491/starts"; cur, new = f"{S}/q170000_m89r491.txt", f"{S}/q170000_m89r491.new"
old = {" ".join(l.split()[2:]) for l in open(cur) if l.startswith("COVER")}; nw = {" ".join(l.split()[2:]) for l in open(new) if l.startswith("COVER")}
if len(nw) == 3924 and nw <= old:
    if not os.path.exists(f"{S}/q170000_m89r491_bbc8cd8_all.txt"):
        shutil.copy2(cur, f"{S}/q170000_m89r491_bbc8cd8_all.txt")
    os.replace(new, cur); print("[s491] installed family B only:", len(nw), "covers (was", len(old), ")")
else:
    print("[s491] NOT installed:", len(nw), "subset", nw <= old)
