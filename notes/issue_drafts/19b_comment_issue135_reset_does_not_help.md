# Comment draft for issue #135 — reset() does not fix the repeated-run crash

**Target:** [Nidhikhare12/OsdagBridge#135](https://github.com/Nidhikhare12/OsdagBridge/issues/135)

---

Additional evidence: calling `reset()` (the app's unlock entry point: `backend.reset()` → `self.memory.release()`) between design runs does **not** fix the crash.

Loop of 5 runs on one `PlateGirderBridge` object, default span-30/cw-10.5 bridge, calling `b.reset()` before each run after the first (`scripts/stress_runs.py`, `evidence/logs/trackL_stress.log`):
- run 1: **ok** (mu_applied 2646.84, flexure 23.06), wall 58 s, RSS ~357 MB (KB units in log)
- run 2: **ValueError: math domain error** at the same LTB `irc22_2015.py:639` site
- runs 3–5: same crash each time

So `reset()`/`memory.release()` is insufficient — the stale state that causes the LTB radicand to go negative is NOT released by `reset()`. This matters because the desktop unlock/redesign path calls `backend.reset()` before re-running Design (see `template_page.py` / `input_dock.py`), so the user-facing "unlock then Design again" flow is expected to hit this on the 2nd run.

Also observed: peak RSS grew monotonically across the 5 attempts (~357→429 MB in the log's KB units) even though only run 1 completed — worth checking whether per-run state/objects accumulate in addition to the crash.

Suggest updating #135 to note that `reset()` is not a workaround, and that the real fix must reset the section/DTO/check state that `compute_buckling_resistance` reads.
