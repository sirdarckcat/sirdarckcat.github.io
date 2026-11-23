# Replacing a runtime that hit Colab's 24 h limit

Colab ends every runtime 24 h after it was created (gold-gpu: created 2026-11-22T19:12:40Z, ended 2026-11-23T19:13:03Z). Before a card ends, `../runlogs/snap.py` packs its
state into `/content/snap.tgz` (trees, envs, scripts, campaign logs, generator ledgers, CPU shares; not the regenerable vector chunks), which is downloaded and kept.

A replacement session (same accelerator) gets the old card's `snap.tgz` and:

- RTX PRO 6000 (G4): `cover491.tgz`, `vecgen491.sh`, `rowguard491.py`, `rowguard491.sh`, then `bash bringup_rtx491.sh PART` (gold-g4 0, gold-g4b 1, gold-g4c 2).
  It restores, runs the production known case on the new GPU (`kc_prod.sh`, 23/23 or stop), and starts the lead's approved 491-family generator for the partition
  (`/content/vec491`, names `q170000_m89r491_p<P>c<seq>`, cap 1,248-1,250, its own ledger).
  - The campaign starts in a fresh directory, `/content/c170r` (vector mode, production's `next_campaign_env` and `deep_env_v89`).
  - The row guard's base is taken after 2,000 vectors.
  - The 463 generator and its ledgers stay in `/content/cover89` for a revert.
- L4 / T4: `kc_m88f.json`, then `bash bringup_l4.sh`. It restores and runs `opl4gate2.sh` on the new GPU against the uaB originals: per-member identity, and
  the m88f known case 40/40 or stop. It then resumes the campaign in `/content/c170f` with its done set, through `deploy_l4op.py` (options, one-pass,
  KLO top-16, any top-up file).
- A new L4 for a card whose state was lost (gold-gpu → gold-l4d): another L4's snapshot as the template, the lost card's untouched share as
  `/content/m88f_gpu_share.json`, then `bash bringup_l4new.sh`. It uses a fresh campaign directory, `/content/c170g`, and blanks the template's top-up files.
  It then runs the same `opl4gate2.sh` check, and `deploy_l4op.py`.

The steps are scripted:

- `handover.sh OLD NEW GPU KIND PART DEADLINE` handles a card that ends on its own. It waits for the final snapshot and for the old session to leave
  `colab sessions`, retries `colab new` while Colab refuses a fourth G4, uploads the kit, starts the bring-up through `launch_bu.py`, and follows
  `/content/bringup.log` through `peek_bu.py`.
- `handover_pro.sh OLD NEW GPU KIND ARG AT` is the proactive form, run at ~23 h (the lead, 19:27Z). At time AT, it waits for a batch end on OLD and stops
  the campaign there. It then takes the final snapshot, pulls the found lines one last time, stops the session to free its slot, and continues as above.
  For KIND `l4new`, ARG is the new card's share file.
