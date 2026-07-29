"""WP9 AlphaEvolve driver: create / start / step the falsification search.

Client-evaluated loop (Discovery Engine v1alpha):
  acquirePrograms -> run each candidate SANDBOXED -> harvest emitted schema
  JSON -> grade with the trusted scorer in a fresh interpreter ->
  submitProgramsEvaluations.

Nothing a candidate program says about its own quality is believed: the only
thing read from a candidate is the schema JSON it prints (harness.md).

Usage:
  ae_runner.py create      # create the experiment (idempotent via state file)
  ae_runner.py start       # start it
  ae_runner.py step [n]    # one acquire/evaluate/submit round (default 8)
  ae_runner.py status      # experiment state + best-so-far board

Credentials: ALPHAEVOLVE_ADC_JSON env var (an ADC authorized_user blob), or
an existing GOOGLE_APPLICATION_CREDENTIALS file. Never committed.
"""

import json
import os
import resource
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "ae_state.json")
SEED = os.path.join(HERE, "ae_seed_program.py")
FINDINGS = os.path.join(HERE, "ae_findings.jsonl")

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "sdcpocs")
ROOT = "https://discoveryengine.googleapis.com/v1alpha/"
ENGINE = ("projects/{}/locations/global/collections/default_collection/"
          "engines/goldbach_1784979910032").format(PROJECT)

CPU_LIMIT = 60            # seconds of CPU per candidate program
MEM_LIMIT = 2 << 30       # 2 GiB address space per candidate
WALL_LIMIT = 90           # wall-clock seconds per candidate
OUT_LIMIT = 4 << 20       # 4 MiB of stdout per candidate
MAX_SCHEMAS = 4000        # graded per candidate


# ---------------------------------------------------------------- auth/http
def _creds():
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    blob = os.environ.get("ALPHAEVOLVE_ADC_JSON")
    if blob and not (path and os.path.exists(path)):
        path = os.path.join(tempfile.gettempdir(), "wp9_adc.json")
        with open(path, "w") as f:
            f.write(blob)
        os.chmod(path, 0o600)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
    import google.auth
    import google.auth.transport.requests as tr
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(tr.Request())
    return creds


_C = {"creds": None, "at": 0.0}


def token():
    if _C["creds"] is None or time.time() - _C["at"] > 1800:
        _C["creds"] = _creds()
        _C["at"] = time.time()
    return _C["creds"].token


def api(rel, method="GET", body=None):
    import urllib.error
    import urllib.request
    url = rel if rel.startswith("http") else ROOT + rel.lstrip("/")
    hdr = {"Authorization": "Bearer " + token(),
           "x-goog-user-project": PROJECT}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        hdr["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdr, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as f:
            return json.load(f)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(raw)["error"]["message"]
        except Exception:
            msg = raw[:400]
        raise SystemExit("API %s %s -> HTTP %s: %s" % (method, url, e.code, msg))


def state(update=None):
    st = {}
    if os.path.exists(STATE):
        st = json.load(open(STATE))
    if update:
        st.update(update)
        json.dump(st, open(STATE, "w"), indent=1)
    return st


# ------------------------------------------------------- sandboxed grading
def _limits():
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_LIMIT, CPU_LIMIT))
    resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT, MEM_LIMIT))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1 << 20, 1 << 20))


def run_candidate(source):
    """Execute candidate source in a locked-down subprocess; return the
    schema dicts it printed (never anything else it claims)."""
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "program.py")
        with open(path, "w") as f:
            f.write(source)
        env = {"PATH": "/usr/bin:/bin", "HOME": td, "PYTHONHASHSEED": "0",
               "no_proxy": "*", "NO_PROXY": "*"}     # no network egress
        try:
            p = subprocess.run([sys.executable, "-I", "program.py"],
                               cwd=td, env=env, preexec_fn=_limits,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               timeout=WALL_LIMIT)
        except subprocess.TimeoutExpired:
            return [], "timeout"
        out = p.stdout[:OUT_LIMIT].decode("utf-8", "replace")
        schemas, bad = [], 0
        for line in out.splitlines():
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                s = json.loads(line)
                if isinstance(s, dict) and "family" in s:
                    schemas.append(s)
                else:
                    bad += 1
            except Exception:
                bad += 1
            if len(schemas) >= MAX_SCHEMAS:
                break
        note = "rc=%d schemas=%d unparsed=%d" % (p.returncode, len(schemas), bad)
        if not schemas and p.stderr:
            note += " stderr=" + p.stderr[:200].decode("utf-8", "replace")
        return schemas, note


def grade(schemas):
    """Grade schemas with the trusted scorer in a FRESH interpreter."""
    if not schemas:
        return {"fitness": 0.0, "killable": 0, "nats": None, "best": None,
                "n": 0, "passes": []}
    code = (
        "import json,sys; sys.path.insert(0, %r); import scorer; scorer.setup();"
        "rows=[scorer.evaluate(s) for s in json.load(sys.stdin)];"
        "print(json.dumps(rows,default=str))" % HERE)
    p = subprocess.run([sys.executable, "-c", code],
                       input=json.dumps(schemas).encode(),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       timeout=900)
    if p.returncode != 0:
        return {"fitness": 0.0, "killable": 0, "nats": None, "best": None,
                "n": 0, "passes": [],
                "err": p.stderr[:300].decode("utf-8", "replace")}
    rows = json.loads(p.stdout.decode())
    rows.sort(key=lambda r: -(r.get("fitness") or 0.0))
    best = rows[0]
    return {"fitness": float(best.get("fitness") or 0.0),
            "killable": int(best.get("killable") or 0),
            "nats": best.get("nats_per_residual_kill"),
            "best": best, "n": len(rows),
            "passes": [r for r in rows if r.get("verdict") == "PASS"]}


def scores_of(g):
    """Metric list submitted to AlphaEvolve. Every number here comes from the
    trusted scorer, never from the candidate."""
    return [
        {"metric": "fitness", "score": float(g["fitness"])},
        {"metric": "killable", "score": float(g["killable"])},
        {"metric": "neg_nats_per_kill",
         "score": -float(g["nats"]) if g["nats"] else -1e6},
    ]


# --------------------------------------------------------------- commands
CONFIG = {
    "title": "WP9 Divisor-Paradigm Closure: certificate-schema falsification",
    "problemDescription": (
        "Evolve propose_schemas() to emit candidate compositeness-certificate "
        "schemas in the fixed grammar L. Goal: find a schema that certifies "
        "more than 1048 (= 3*sqrt(Q)) DISTINCT prime offsets q < Q = 122,000 "
        "composite for a constructible family of even N < 10^200, at a "
        "marginal design-entropy cost below 1.01 nats per residual kill (the "
        "measured covering endgame). Such a schema would falsify the "
        "Divisor-Paradigm Closure Theorem; 13,661 hand-enumerated schemas "
        "found none. Print ONLY schema JSON lines: kills and costs are "
        "measured externally by a trusted scorer, so self-reported quality is "
        "ignored. Primary metric 'fitness' in [0,1] is "
        "min(1,killable/1048)*min(1,1.01/nats_per_residual_kill); 1.0 means "
        "the theorem is broken. Secondary metrics show which half is binding."),
    "programLanguage": "python",
    "runSettings": {"maxPrograms": 100, "concurrency": 6,
                    "maxDuration": "86400s"},
    "generationSettings": {
        "includeFullProgramInPrompt": True,
        "models": [{"name": "gemini-3.1-pro-preview", "weight": 0.7},
                   {"name": "gemini-3.5-flash", "weight": 0.3}]},
}


SESSION_LABEL = "WP9 closure falsification"


def cmd_create():
    """Create experiment (config only -- initialAlphaEvolveProgram is output
    only), then POST the seed program under it, then it is ready to start."""
    st = state()
    if st.get("experiment"):
        print("experiment already recorded:", st["experiment"])
        return 0
    sname = st.get("session")
    if not sname:                       # reuse our session if one exists
        for s in api(ENGINE + "/sessions").get("sessions", []):
            if s.get("displayName") == SESSION_LABEL:
                sname = s["name"]
                break
    if not sname:
        sname = api(ENGINE + "/sessions", "POST",
                    {"displayName": SESSION_LABEL, "state": "IN_PROGRESS"})["name"]
    name = None
    for e in api(sname + "/alphaEvolveExperiments").get(
            "alphaEvolveExperiments", []):
        if (e.get("config") or {}).get("title") == CONFIG["title"]:
            name = e["name"]
            break
    if not name:
        exp = api(sname + "/alphaEvolveExperiments", "POST", {"config": CONFIG})
        name = exp.get("name") or exp.get("response", {}).get("name")
    # a new program must be posted WITH at least one score, so grade the seed
    src = open(SEED).read()
    schemas, note = run_candidate(src)
    g = grade(schemas)
    print("seed graded locally: %s -> fitness %.4f (killable=%s nats=%s)"
          % (note, g["fitness"], g["killable"], g["nats"]))
    seed = api(name + "/alphaEvolvePrograms", "POST",
               {"content": {"description": "WP9 seed: schema proposer",
                            "files": [{"path": "program.py",
                                       "programLanguage": "python",
                                       "content": src}]},
                "evaluation": {"scores": {"scores": scores_of(g)}}})
    state({"session": sname, "experiment": name,
           "seed_program": seed.get("name"), "created": time.time()})
    print("session:   ", sname)
    print("experiment:", name)
    print("seed:      ", seed.get("name"))
    return 0


def cmd_start():
    st = state()
    exp = st["experiment"]
    r = api(exp + ":start", "POST", {})
    print("start ->", json.dumps(r)[:300])
    return 0


def cmd_status():
    st = state()
    d = api(st["experiment"])
    print("state:", d.get("state"), "| stats:", json.dumps(d.get("stats"))[:300])
    if os.path.exists(FINDINGS):
        rows = [json.loads(l) for l in open(FINDINGS)]
        # Rows logged before the 2026-07-29 budget-accounting fix used the old
        # (unbudgeted) scorer, so their fitness is not comparable. Detect them
        # by the absence of the budget cap: claimed coverage without a cap.
        live = [r for r in rows if (r.get("killable") or 0) <= 2000]
        stale = len(rows) - len(live)
        live.sort(key=lambda r: -r["fitness"])
        print("graded candidates: %d (%d pre-fix rows hidden) | best fitness %.4f"
              % (len(rows), stale, live[0]["fitness"] if live else 0.0))
        for r in live[:5]:
            b = r.get("best") or {}
            print("   fitness %.4f eff_offsets=%s nats/offset=%s  %s %s" %
                  (r["fitness"], r.get("killable"), r.get("nats"),
                   b.get("family", "?"), json.dumps(b.get("params"))[:60]))
        print("   bar to beat: covering's average 0.041 nats/offset, "
              "and >%d effective offsets" % 1048)
    return 0


def cmd_step(n):
    st = state()
    exp = st["experiment"]
    got = api(exp + ":acquirePrograms", "POST", {"desiredProgramsCount": n})
    progs = got.get("programs") or got.get("alphaEvolvePrograms") or []
    print("acquired %d program(s)" % len(progs), flush=True)
    if not progs:
        d = api(exp)
        print("experiment state:", d.get("state"))
        return 0
    evals = []
    for p in progs:
        files = (p.get("content") or {}).get("files") or []
        src = files[0].get("content", "") if files else ""
        schemas, note = run_candidate(src)
        g = grade(schemas)
        pid = p.get("name", "?").split("/")[-1]
        print("  %s: %s -> fitness %.4f (killable=%s nats=%s)" %
              (pid, note, g["fitness"], g["killable"], g["nats"]), flush=True)
        with open(FINDINGS, "a") as f:
            f.write(json.dumps({"program": p.get("name"), "note": note,
                                **{k: g[k] for k in
                                   ("fitness", "killable", "nats", "n")},
                                "best": g.get("best")}) + "\n")
        if g["passes"]:
            print("  !!! PASS -- halting for hand audit:",
                  json.dumps(g["passes"][:2])[:600], flush=True)
            state({"halted_pass": p.get("name")})
            return 3
        api(exp + ":submitProgramsEvaluations", "POST",
            {"evaluationSubmissions": [{
                "program": p.get("name"),
                "evaluation": {"scores": {"scores": scores_of(g)}},
                "lockToken": p.get("lockToken")}]})
        evals.append(p.get("name"))
    print("submitted %d evaluation(s)" % len(evals), flush=True)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "create":
        sys.exit(cmd_create())
    if cmd == "start":
        sys.exit(cmd_start())
    if cmd == "step":
        sys.exit(cmd_step(int(sys.argv[2]) if len(sys.argv) > 2 else 8))
    sys.exit(cmd_status())
