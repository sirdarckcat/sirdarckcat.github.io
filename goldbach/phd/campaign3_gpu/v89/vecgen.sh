#!/bin/bash
# Keep 89-moduli vectors (covers on the first 89 odd primes, Q = 170,000) ahead of the vector campaign on this card: whenever fewer than AHEAD vectors are
# left unconsumed (written to V/vec_*.json minus slices in the campaign's search.log), a covergen walk (cap CAP, a new seed each time) from the research
# session's starts/q170000_m89.txt, this card's share of the covers (part.py: md5 mod NPART == PART), make_specs.py (kmax auto, best first, this card's
# ledger: no vector twice) and check_specs.py (an independent recheck from N0 and M) make a chunk of up to CHUNK vectors, published by an atomic rename.
# If a walk gives no new vector, CAP goes up by one (up to CAPMAX).
#   nohup bash vecgen.sh V CAMPAIGN_DIR PART NPART > vecgen.log 2>&1 &
C=${COVER_DIR:-/content/cover89}; V=$1; CAMP=$2; PART=$3; NPART=$4
CAP=${CAP:-1250}; CAPMAX=${CAPMAX:-1253}; CHUNK=${CHUNK:-1000}; AHEAD=${AHEAD:-12000}
mkdir -p $V; cd $C || exit 1
[ -x ./covergen ] || gcc -O3 -march=native -fopenmp -o covergen covergen.c -lm || exit 1
seq=$(ls $V 2>/dev/null | grep -c '^vec_.*[.]json$')
[ -s $V/made.txt ] || python3 -c "import glob, json, sys; print(sum(len(json.load(open(f))) for f in glob.glob(sys.argv[1] + '/vec_*.json')))" $V > $V/made.txt
while true; do
  made=$(cat $V/made.txt)
  used=$(grep -c '^\[q170000_m89' $CAMP/search.log 2>/dev/null); used=${used:-0}
  if [ $((made - used)) -ge $AHEAD ]; then sleep 30; continue; fi
  seed=$((PART * 1000003 + seq * 7919 + 17))
  t0=$(date +%s)
  OMP_NUM_THREADS=${OMP_THREADS:-4} ./covergen 170000 starts/q170000_m89.txt $CAP $((CHUNK * NPART * 3 + 2000)) $seed > walk.tmp 2> walk.err
  python3 part.py walk.tmp $PART $NPART > walk.part
  name=$(printf "p%dc%05d" $PART $seq)
  if python3 make_specs.py 170000 q170000_m89_$name auto walk.part chunk.tmp.json $CHUNK $CAP ledger_p$PART.txt > make.out 2>&1 && python3 check_specs.py chunk.tmp.json > check.out 2>&1; then
    n=$(tail -n 1 make.out | awk '{print $1}')
    mv chunk.tmp.json $V/vec_$(printf %06d $seq).json && echo $((made + n)) > $V/made.txt
    echo "$(date -u +%FT%TZ) chunk $seq: $(tail -n 1 make.out | cut -c1-160) | $(tail -n 1 check.out | cut -c1-120) | $(( $(date +%s) - t0 )) s"
    seq=$((seq + 1))
  else
    echo "$(date -u +%FT%TZ) no chunk at cap $CAP: $(tail -n 1 make.out | cut -c1-200) $(tail -n 1 check.out | cut -c1-200)"
    if [ $CAP -lt $CAPMAX ]; then CAP=$((CAP + 1)); echo "cap raised to $CAP"; else sleep 300; fi
  fi
done
