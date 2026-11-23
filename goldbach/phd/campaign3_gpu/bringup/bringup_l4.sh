#!/bin/bash
# Bring up a replacement L4 / T4 for a card that hit Colab's 24 h limit, on the configuration of 23 Nov ~19:15Z: the old card's snapshot (/content/snap.tgz: trees c3g, ua_v10
# (uaB + f1b904a + fc12768's gbig.py), uaB, f29fr; next_campaign_env / deep_env with their *_pre_l4op originals; c170f's search.log (the done slices) and my_specs.json; the
# m88f top-up files; run_v5_campQ.sh, deploy_l4op.py, opl4gate2.sh) and /content/kc_m88f.json.
# Steps: restore, install gmpy2, opl4gate2.sh on this GPU (per-member identity base/new at production f + the m88f known case 40/40, or stop), then deploy_l4op.py (OPTIONS=1:
# the options, one-pass, KLO top-16, any top-up file not yet appended), which starts the campaign in c170f with its done set. Log: /content/bringup.log
L=/content/bringup.log
echo "$(date -u +%FT%TZ) bring-up start, $(hostname), $(nvidia-smi --query-gpu=name --format=csv,noheader)" >> $L
cd /content && tar -xzf /content/snap.tgz --exclude="bringup*" >> $L 2>&1 || { echo "BRINGUP-FAILED restore" >> $L; exit 1; }
python3 -c 'import gmpy2' 2>/dev/null || pip install -q gmpy2 >> $L 2>&1
python3 -c 'import gmpy2, cupy; print("gmpy2", gmpy2.version(), "cupy", cupy.__version__)' >> $L 2>&1
echo "$(cat /content/next_campaign_dir 2>/dev/null)" | grep -q c170f || echo "/content/c170f" > /content/next_campaign_dir
# opl4gate2.sh compares against production's base tree (uaB) and needs the env without the options: use the *_pre_l4op originals for its base runs
cp /content/next_campaign_env /content/next_campaign_env_deployed; cp /content/deep_env /content/deep_env_deployed
cp /content/next_campaign_env_pre_l4op /content/next_campaign_env; cp /content/deep_env_pre_l4op /content/deep_env
bash /content/opl4gate2.sh >> $L 2>&1
cat /content/opl4g2/result.txt >> $L 2>/dev/null
grep -q "L4-GATE2 PASSED" /content/opl4g2/result.txt || { echo "BRINGUP-FAILED per-member / known-case check on this GPU" >> $L; cp /content/next_campaign_env_deployed /content/next_campaign_env; cp /content/deep_env_deployed /content/deep_env; exit 1; }
pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign '; sleep 5
C=$(cat /content/next_campaign_dir); touch $C/gpu3_stats.log $C/search.log; [ -f /content/ua10_cuda.tgz ] || { echo "BRINGUP-FAILED /content/ua10_cuda.tgz missing (upload ua10b_cuda.tgz with the snapshot)" >> $L; exit 1; }
python3 /content/deploy_l4op.py >> $L 2>&1
echo BRINGUP-DONE >> $L
