# Single-case executor. Runs in a subprocess with RLIMIT_AS set by the parent.
import argparse, json, os, resource, sys, time, traceback, hashlib

MEM_LIMIT = int(os.environ.get("XRUN_MEM_BYTES", 4 * 1024**3))

def set_mem():
    try:
        resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT, MEM_LIMIT))
    except Exception as e:
        sys.stderr.write(f"[run_one] setrlimit(RLIMIT_AS, {MEM_LIMIT}) unavailable on this host: {e}\n")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("case_id")
    p.add_argument("--json-out", default="")
    args = p.parse_args()
    set_mem()
    sys.path.insert(0, "/Users/macbook/Projects/OsdagBridge/src")
    sys.path.insert(0, "/Users/macbook/Projects/osdagbridge-testing-report")
    t0 = time.time()
    rec = dict(id=args.case_id, status="ERROR", runtime=0.0, peak_mb=0.0,
               exception_type="", innermost_frame="", message="", input_file="",
               traceback_sig="", oracle="")
    try:
        from tests.extreme import registry
        c = next(c for c in registry.CASES if c["id"] == args.case_id)
        rec["oracle"] = c["oracle"]
        rec["layer"] = c["layer"]
        d = c["fn"]()
        rec["input_file"] = d if isinstance(d, str) else d.get("_tmp_file", "")
        oracle = c["oracle"]
        if isinstance(oracle, str):
            import tests.extreme.oracles as _or
            oracle = getattr(_or, oracle)
        oracle(d)
        rec["status"] = "PASS"
    except SystemExit as e:
        rec["status"] = "ERROR"; rec["exception_type"] = "SystemExit"
        rec["message"] = str(e)
    except BaseException as e:
        rec["status"] = "FAIL"
        rec["exception_type"] = type(e).__name__
        tb = traceback.format_exc()
        rec["message"] = str(e)[:300]
        frames = [l for l in tb.splitlines() if l.startswith('  File "/Users/macbook/Projects/OsdagBridge')]
        if frames:
            rec["innermost_frame"] = frames[-1].strip()[:300]
        sig = " | ".join(l.strip()[:80] for l in tb.splitlines() if l.strip().startswith(("ValueError", "TypeError", "KeyError", "AttributeError", "AssertionError", "RuntimeError", "OverflowError", "IndexError", "ZeroDivisionError")))
        rec["traceback_sig"] = (sig or rec["message"])[:400]
    finally:
        rec["runtime"] = round(time.time() - t0, 3)
        try:
            import psutil
            rec["peak_mb"] = round(psutil.Process().memory_info().rss / 1e6, 1)
        except Exception:
            pass
    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump(rec, f)
    print(json.dumps(rec))

if __name__ == "__main__":
    main()
