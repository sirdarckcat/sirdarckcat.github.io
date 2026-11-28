#!/bin/bash
# (vecgen491.sh: research's 491-family covers, bbc8cd8, cover dir /content/cover491, names q170000_m89r491_p<P>c<seq>, cap 1,248 to 1,250.)
# Keep 89-moduli vectors (covers on the first 89 odd primes, Q = 170,000) ahead of the vector campaign on this card: whenever fewer than AHEAD vectors are
# left unconsumed (written to V/vec_*.json minus slices in the campaign's search.log), a covergen walk (cap CAP, a new seed each time) from the research
# session's starts/q170000_m89r491.txt, this card's share of the covers (part.py: md5 mod NPART == PART), make_specs.py (kmax auto, best first, this card's
# ledger: no vector twice) and check_specs.py (an independent recheck from N0 and M) make a chunk of up to CHUNK vectors, published by an atomic rename.
# If a walk gives no new vector, CAP goes up by one (up to CAPMAX). The lead (23 Nov 21:46Z): also when a walk gives fewer than YMIN = 100 new vectors (the
# leftovers at the old cap still come out of later walks, best first), and at once when fewer than BUFMIN (~10 min of an RTX's supply) are ahead after a walk that
# did not fill its chunk: a GPU must never wait for vectors. Each step is logged as its own line "cap raised to N" (the row guard steps its base on these).
#   nohup bash vecgen.sh V CAMPAIGN_DIR PART NPART > vecgen.log 2>&1 &
C=${COVER_DIR:-/content/cover491}; V=$1; CAMP=$2; PART=$3; NPART=$4
CAP=${CAP:-1248}; CAPMAX=${CAPMAX:-1250}; CHUNK=${CHUNK:-1000}; AHEAD=${AHEAD:-12000}; YMIN=${YMIN:-100}; BUFMIN=${BUFMIN:-3500}
mkdir -p $V; cd $C || exit 1
[ -x ./covergen ] || gcc -O3 -march=native -fopenmp -o covergen covergen.c -lm || exit 1
# the next chunk number: above every chunk in V and, on a card that replaced another, at least V/seq0.txt (written by the bring-up from the old card's logs), so no name is reused
seq=$(ls $V 2>/dev/null | sed -n 's/^vec_0*\([0-9][0-9]*\)[.]json$/\1/p' | sort -n | tail -n 1); seq=$(( ${seq:--1} + 1 ))
[ -s $V/seq0.txt ] && [ "$(cat $V/seq0.txt)" -gt "$seq" ] && seq=$(cat $V/seq0.txt)
[ -s $V/made.txt ] || python3 -c "import glob, json, sys; print(sum(len(json.load(open(f))) for f in glob.glob(sys.argv[1] + '/vec_*.json')))" $V > $V/made.txt
while true; do
  made=$(cat $V/made.txt)
  used=$(grep -c '^\[q170000_m89r491' $CAMP/search.log 2>/dev/null); used=${used:-0}
  if [ $((made - used)) -ge $AHEAD ]; then sleep 30; continue; fi
  seed=$((PART * 1000003 + seq * 7919 + 17))
  t0=$(date +%s)
  OMP_NUM_THREADS=${OMP_THREADS:-4} ./covergen 170000 starts/q170000_m89r491.txt $CAP $((CHUNK * NPART * 3 + 2000)) $seed > walk.tmp 2> walk.err
  python3 part.py walk.tmp $PART $NPART > walk.part
  name=$(printf "p%dc%05d" $PART $seq)
  if python3 make_specs.py 170000 q170000_m89r491_$name auto walk.part chunk.tmp.json $CHUNK $CAP ledger_p$PART.txt > make.out 2>&1 && python3 check_specs.py chunk.tmp.json > check.out 2>&1; then
    n=$(tail -n 1 make.out | awk '{print $1}')
    mv chunk.tmp.json $V/vec_$(printf %06d $seq).json && echo $((made + n)) > $V/made.txt
    echo "$(date -u +%FT%TZ) chunk $seq: $(tail -n 1 make.out | cut -c1-160) | $(tail -n 1 check.out | cut -c1-120) | $(( $(date +%s) - t0 )) s"
    seq=$((seq + 1))
    ahead=$((made + n - used))
    if [ $CAP -lt $CAPMAX ] && { [ "$n" -lt $YMIN ] || { [ "$n" -lt $CHUNK ] && [ $ahead -lt $BUFMIN ]; }; }; then
      CAP=$((CAP + 1)); echo "$(date -u +%FT%TZ) low yield: the walk gave $n new vectors (fewer than $YMIN, or $ahead ahead < $BUFMIN): the cap steps"; echo "cap raised to $CAP"
    fi
  else
    echo "$(date -u +%FT%TZ) no chunk at cap $CAP: $(tail -n 1 make.out | cut -c1-200) $(tail -n 1 check.out | cut -c1-200)"
    if [ $CAP -lt $CAPMAX ]; then CAP=$((CAP + 1)); echo "cap raised to $CAP"; else sleep 300; fi
  fi
done
