# Upload code + state to a fresh GPU session ($1 = session name). Every call has a hard timeout.
export PATH="$HOME/.local/bin:$PATH"; S=$1
P=/home/user/sirdarckcat.github.io/goldbach/proth; R=$P/runs; SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad
up() { timeout 300 colab upload -s $S "$1" "$2" < /dev/null 2>&1 | grep -v -i keyring | grep -q Uploaded && echo "up $2" || echo "UPLOAD FAILED $2"; }
for f in gpu_screen.py gpu_search.py desert.py deep_sieve.py deepsieve.c cpu_search.py; do up $P/$f /content/$f; done
up $SP/spec2m.json /content/spec2m.json; up $SP/spec12_inc.json /content/spec12_inc.json
up $R/q10000000/spec.json /content/q1e7_spec.json
up $R/q10000000/survivors_T32768_B100000000000.json /content/q1e7_surv.json
up $R/q10000000/gpu_tests.jsonl /content/q1e7/tests.jsonl
up $R/q16045849/spec.json /content/q16m_spec.json
up $R/q16045849/survivors_T32768_B100000000000.json /content/q16m_surv.json
up $R/q16045849/q16m_surv_cpu.kills.json /content/q16m_surv.cpu.kills.json
up $R/q16045849/colab_cpu_helper_tests.jsonl /content/q16m_cpu/tests.jsonl
up $SP/colab/q16m_cpu_helper_plus.jsonl /content/q16m_cpu_helper.jsonl
up $SP/colab/queue4.sh /content/queue4.sh
up $SP/colab/gpu_kat.py /content/gpu_kat.py
