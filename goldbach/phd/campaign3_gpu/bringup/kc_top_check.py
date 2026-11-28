import json, os
REF = [(20899461, 48589), (20903013, 52237), (20909356, 46327), (20914784, 51001), (20922075, 56809), (20924406, 47389), (20928592, 49669), (20929390, 50131), (20938947, 48589), (21044951, 56377), (21050303, 52021), (21138137, 49477), (21148982, 47221), (21154485, 47317), (21163509, 46327), (21193180, 52627), (21200833, 54181), (21214016, 49639), (21230683, 51607), (21233580, 48871), (21234843, 46441), (21246122, 55381), (21276261, 50821), (21314491, 46441), (21331195, 48049)]
f = "/content/kc_prod/camp/found.jsonl"
nm = sorted((int(x["k"]), int(x["g"])) for x in (json.loads(l[l.index("{"):]) for l in (open(f) if os.path.exists(f) else []) if l.strip()))
ok = nm == REF
print(f"[kt] known case at the TOP window (production placement): {len(nm)} near-misses, identical to the CPU brute force's 25 (vtop/knowncase_top_cpu_brute.txt): {ok}")
print("[kt] KCTOP", "PASSED" if ok else "FAILED")
