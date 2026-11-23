import os, json
C = open("/content/next_campaign_dir").read().split()[0]
print("[pre]", os.popen("hostname").read().strip(), "| dir", C, "| procs", os.popen(f"pgrep -fc 'search_gpu5[.]py --campaign {C} '").read().strip(),
      "| runner", os.popen("pgrep -fc 'run_v5_campQ[.]sh'").read().strip(),
      "| files", [f for f in ("/content/run_v5_campQ.sh", "/content/next_campaign_env", "/content/deep_env", "/content/m88f_share.json", "/content/deploy_m88f.py", "/content/c170f") if os.path.exists(f)])
if os.path.exists("/content/m88f_share.json"):
    s = json.load(open("/content/m88f_share.json")); print("[pre] share", len(s), s[0]["name"], s[-1]["name"])
print("[pre] env", open("/content/next_campaign_env").read().strip()[:300])
print("[pre] deep", open("/content/deep_env").read().strip()[:300])
print("[pre] stats tail", open(C + "/gpu3_stats.log").read().splitlines()[-1][:200] if os.path.exists(C + "/gpu3_stats.log") else None)
