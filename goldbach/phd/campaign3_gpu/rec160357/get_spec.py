import json
f = [json.loads(l) for l in open("/content/c170r/found.jsonl") if l.strip()]
hit = [x for x in f if x.get("g") == 160357]
assert len(hit) == 1, len(hit)
h = hit[0]; base = h["name"].split("@")[0]
c = int(base.split("_")[2].split("c")[1])
spec = [s for s in json.load(open(f"/content/vec491/vec_{c:06d}.json")) if s["name"] == base]
assert len(spec) == 1
json.dump(h, open("/content/rec160357_found.json", "w")); json.dump(spec, open("/content/rec160357_spec.json", "w"))
print("[gs] ok", base, "chunk", c, "| found keys", sorted(h.keys()), "| spec keys", sorted(spec[0].keys()))
