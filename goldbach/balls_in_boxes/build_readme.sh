#!/bin/sh
# README.md = README.in with the tables from make_tables.py in place of the line TABLES; T3.md likewise from T3.in and make_t3.py
set -e
cd "$(dirname "$0")"
python3 make_tables.py > tables.md
python3 make_t3.py > t3_tables.md
python3 -c "
for src, tab, dst in (('README.in', 'tables.md', 'README.md'), ('T3.in', 't3_tables.md', 'T3.md')):
    t = open(src).read(); tb = open(tab).read().rstrip()
    assert t.count('TABLES') == 1
    open(dst, 'w').write(t.replace('TABLES', tb))"
