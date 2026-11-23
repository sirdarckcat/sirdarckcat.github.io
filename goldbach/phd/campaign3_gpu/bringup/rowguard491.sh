#!/bin/bash
# The lead's row-count guard for f = 0.985 (rowguard491.py) every 5 minutes until it trips; log /content/rowguard491.log.
while true; do timeout 600 python3 /content/rowguard491.py >> /content/rowguard491.log 2>&1; [ -e /content/rowguard491_tripped.txt ] && break; sleep 300; done
