#!/bin/bash
# The lead's row-count guard for f = 0.985 (rowguard.py) every 5 minutes until it trips; log /content/rowguard.log.
while true; do timeout 600 python3 /content/rowguard.py >> /content/rowguard.log 2>&1; [ -e /content/rowguard_tripped.txt ] && break; sleep 300; done
