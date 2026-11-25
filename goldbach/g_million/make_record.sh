#!/bin/bash
# T5: turn a hit into a record directory record_<digits>digit/: N, the cover, the independent check from N alone (verify.py: factors
# up to 10^6 or a failed Fermat test for every N - q, then g by BPSW), the compositeness certificate (certificate.py: a modulus, the
# least prime factor up to B, or a failed Fermat test for every row; checked against the sieve's survivor list), and the test log.
#   ./make_record.sh hit_<tag>_k<k>.json [tag] [cover]
set -e
hit=$1; tag=${2:-d2190}; cover=${3:-hb5113_b1.txt}
digits=$(python3 -c "import json; print(len(json.load(open('$hit'))['N']))")
dir=record_${digits}digit; mkdir -p $dir
python3 -c "import json; print(json.load(open('$hit'))['N'])" > $dir/N.txt
cp "$hit" $dir/hit.json; cp "$cover" $dir/cover.txt; cp setup_$tag.json $dir/setup.json
python3 verify.py $dir/N.txt 2>&1 | tee $dir/verify.log
mv verify_${digits}digit.json $dir/verify.json
python3 certificate.py "$hit" "$cover" $dir/certificate.txt 1000003 1e9 surv_$tag.txt 2>&1 | tee $dir/certificate.log
cp tested_$tag.jsonl $dir/tested.jsonl
echo "record directory: $dir"
