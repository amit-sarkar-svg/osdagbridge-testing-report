# Comment draft for issue #89 — executed node-level root cause, and link to #132

**Target:** [Nidhikhare12/OsdagBridge#89](https://github.com/Nidhikhare12/OsdagBridge/issues/89) (also relevant to #132)

---

Additional executed evidence for the `build_girders()` root cause, and a connection to the skew-sign asymmetry reported in #132.

I built the oblique grillage directly (pure geometry, no design) with `og.create_grillage(..., skew=±15, mesh_type="Oblique")`, span 30 m, width 8.4 m, 4 longitudinal grid lines, and counted how many nodes sit exactly at `min_x` / `max_x` — the values `build_girders()` (analysis_results.py:422-431) uses to define the start/end edges:

```
skew=+15°: min_x=-2.251 -> 1 node at min_x (z=8.4); max_x=30.000 -> 1 node at max_x
skew=-15°: min_x= 0.000 -> 1 node at min_x (z=0.0);   max_x=32.251 -> 1 node at max_x
```

Because the start/end edges are inclined under skew, only a single corner node has the exact extreme x, so `start_nodes`/`end_nodes` each contain one node instead of the full edge. This is exactly why only G1/EB1 survives, matching your table (+15°/−15°: G1 only).

This also explains #132 (skew-sign asymmetry): for +15° the lone start corner is at z=8.4, for −15° it is at z=0.0 — opposite edges. The surviving girder is therefore at the opposite side for the two signs, so load-driven utilizations differ (and the direction of the difference flips with geometry). The mesh node coordinates themselves are perfectly mirror-symmetric (x flips sign exactly, e.g. −0.281↔+0.281), so the geometry is fine — the fault is the edge-identification in `build_girders()`.

Suggested fix: identify start/end edges by the *inclined edge line* (all nodes on the first/last transverse grid line), e.g. group by the transverse mesh line index rather than by exact min/max x, so all girders are paired for skewed bridges. Fixing this should resolve both #89 and the girder-mapping component of #132.

Happy to share the node-coordinate dump if useful.
