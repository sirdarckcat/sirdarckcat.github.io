#!/bin/sh
# README.md = README.in with the tables from make_tables.py in place of the line TABLES
set -e
cd "$(dirname "$0")"
python3 make_tables.py > tables.md
python3 -c "
t = open('README.in').read(); tb = open('tables.md').read().rstrip()
assert t.count('TABLES') == 1
open('README.md', 'w').write(t.replace('TABLES', tb))"
