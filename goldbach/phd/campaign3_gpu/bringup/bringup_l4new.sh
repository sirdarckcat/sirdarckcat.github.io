#!/bin/bash
# Bring up a NEW L4 in place of one whose state was lost (gold-gpu, ended 19:13Z before a snapshot): another L4's snapshot as the template (/content/snap.tgz: trees,
# envs and their *_pre_l4op originals, scripts), a fresh campaign dir /content/c170g with the lost card's untouched m88f share (/content/m88f_gpu_share.json: gold-gpu's top3,
# 3,476 vectors; its top2 share is not reused since its done levels were lost), the template's own top-up file blanked (so nothing of the template card's share is appended),
# then opl4gate2.sh on this GPU (per-member identity + the m88f known case 40/40, or stop) and deploy_l4op.py (options, one-pass, KLO top-16). Log: /content/bringup.log
L=/content/bringup.log
echo "$(date -u +%FT%TZ) bring-up start (new L4 or T4, fresh campaign dir c170g, the share in /content/m88f_gpu_share.json), $(hostname), $(nvidia-smi --query-gpu=name --format=csv,noheader)" >> $L
cd /content && tar -xzf /content/snap.tgz --exclude="bringup*" >> $L 2>&1 || { echo "BRINGUP-FAILED restore" >> $L; exit 1; }
python3 -c 'import gmpy2' 2>/dev/null || pip install -q gmpy2 >> $L 2>&1
python3 -c 'import gmpy2, cupy; print("gmpy2", gmpy2.version(), "cupy", cupy.__version__)' >> $L 2>&1
mkdir -p /content/c170g && cp /content/m88f_gpu_share.json /content/c170g/my_specs.json && echo "/content/c170g" > /content/next_campaign_dir
echo "[]" > /content/m88f_top3.json; echo "[]" > /content/m88f_top2.json
python3 -c "import json; s = json.load(open('/content/c170g/my_specs.json')); print(len(s), 'vectors', s[0]['name'], s[-1]['name'])" >> $L
cp /content/next_campaign_env_pre_l4op /content/next_campaign_env; cp /content/deep_env_pre_l4op /content/deep_env
bash /content/opl4gate2.sh >> $L 2>&1
cat /content/opl4g2/result.txt >> $L 2>/dev/null
grep -q "L4-GATE2 PASSED" /content/opl4g2/result.txt || { echo "BRINGUP-FAILED per-member / known-case check on this GPU" >> $L; exit 1; }
pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign '; sleep 5
C=$(cat /content/next_campaign_dir); touch $C/gpu3_stats.log $C/search.log; [ -f /content/ua10_cuda.tgz ] || { echo "BRINGUP-FAILED /content/ua10_cuda.tgz missing (upload ua10b_cuda.tgz with the snapshot)" >> $L; exit 1; }
python3 /content/deploy_l4op.py >> $L 2>&1
echo BRINGUP-DONE >> $L
