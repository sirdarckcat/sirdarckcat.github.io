#!/bin/bash
# comb.sh (the check, campaign paused) then deploy_comb.py (deploys only if the check passed).
bash /content/comb.sh; python3 /content/deploy_comb.py; echo COMBD-DONE
