#!/usr/bin/env python3
"""XRUN: extreme-test driver.
Runs case-registry cases, each in its own subprocess (timeout + RLIMIT_AS),
writes evidence/xrun/results.jsonl. Supports --layers, --ids, --rerun-failed,
--dry-run, --seed (ignored, kept for CLI parity)."""
import argparse, concurrent.futures as cf, json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir("/Users/macbook/Projects/osdagbridge-testing-report")
sys.path.insert(0, os.getcwd())

from tests.extreme import registry

def run_one(case_id):
    js = f"evidence/xrun/one_{case_id}.json"
    os.makedirs("evidence/xrun", exist_ok=True)
    if os.path.exists(js): os.remove(js)
    mem_limit = int(os.environ.get("XRUN_MEM_BYTES", 4 * 1024**3))
    t0 = time.time(); peak = 0
    try:
        import psutil
        p = psutil.Popen([sys.executable, "tests/extreme/run_one.py", case_id, "--json-out", js])
        oom = False
        while True:
            rc = p.poll()
            if rc is None:
                try:
                    rss = p.memory_info().rss
                    peak = max(peak, rss / 1e6)
                    if rss > mem_limit:
                        p.kill(); oom = True
                except Exception: pass
                if time.time() - t0 > 600:
                    p.kill(); rec = dict(id=case_id, status="TIMEOUT", runtime=round(time.time()-t0,1),
                                         peak_mb=round(peak,1), exception_type="TimeoutExpired",
                                         innermost_frame="", message="exceeded 600 s", input_file="",
                                         traceback_sig="TIMEOUT (driver killed)"); return rec
                time.sleep(0.05)
                continue
            break
        rec = dict(id=case_id, status="OOM" if oom else "ERROR",
                   runtime=round(time.time()-t0,2), peak_mb=round(peak,1),
                   exception_type="OOM" if oom else "HARD_CRASH",
                   innermost_frame="", message="killed by driver RSS watchdog" if oom else "(no rec file)",
                   input_file="", traceback_sig="OOM" if oom else "hard crash")
    except Exception as e:
        rec = dict(id=case_id, status="ERROR", runtime=round(time.time()-t0,2), peak_mb=round(peak,1),
                   exception_type="DriverError", innermost_frame="", message=str(e)[:200],
                   input_file="", traceback_sig="driver error")
    # read child record
    if os.path.exists(js):
        rec = json.load(open(js)); rec["peak_mb"] = round(peak if rec.get("peak_mb",0)<peak else rec.get("peak_mb",0),1)
    return rec

def load_prev():
    out = []
    p = "evidence/xrun/results.jsonl"
    if os.path.exists(p):
        for line in open(p):
            try: out.append(json.loads(line))
            except Exception: pass
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layers", default=None)
    ap.add_argument("--ids", default=None)
    ap.add_argument("--tags", default=None)
    ap.add_argument("--rerun-failed", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--parallel", type=int, default=3)
    ap.add_argument("--out", default="evidence/xrun/results.jsonl")
    a = ap.parse_args()

    cases = registry.filter_cases(layer=a.layers, tags=(a.tags.split(",") if a.tags else None),
                                  ids=(a.ids.split(",") if a.ids else None))
    if a.rerun_failed:
        prev = load_prev(); failed = {r["id"] for r in prev if r["status"] not in ("PASS", "SKIPPED")}
        cases = [c for c in cases if c["id"] in failed]

    if a.dry_run:
        for c in cases: print(f"DRYRUN {c['id']}\t{c['layer']}\t{c['oracle']}")
        print(f"total={len(cases)}")
        return

    prev = load_prev()
    os.makedirs("evidence/xrun", exist_ok=True)
    nfail = 0
    with cf.ThreadPoolExecutor(max_workers=a.parallel) as ex:
        results = list(ex.map(run_one, [c["id"] for c in cases]))
    with open(a.out, "a") as f:
        for rec in results:
            f.write(json.dumps(rec) + "\n")
            nfail += 0 if rec["status"] == "PASS" else 1
            print(f"{rec['status']:7s} {rec['id']:40s} {rec['runtime']:7.2f}s  {rec['exception_type'][:24]:24s} {rec['message'][:60]}")
    print(f"SUMMARY cases={len(results)} failures={nfail}")

if __name__ == "__main__":
    main()
