# Reply draft — recheck of #132 on a second machine

**Target:** [Nidhikhare12/OsdagBridge#132](https://github.com/Nidhikhare12/OsdagBridge/issues/132) (reply to Mounil2005's comment)

---

Thanks for the independent reproduction — I re-ran your exact configuration on a second, separate machine (macOS, conda `osdagbridge-env`, same `dev` @ d74f56d) using a headless build of the default bridge (span 30 m, carriageway 7.5 m, 4 girders, Optimized), changing only the skew sign. My numbers match yours **exactly**:

| Result | +15° | −15° | (your table) |
|---|---|---|---|
| Flexure utilisation | 19.49 % | 18.17 % | 19.49 / 18.17 ✓ |
| Shear utilisation | 41.73 % | 53.27 % | 41.73 / 53.27 ✓ |
| Fatigue utilisation | 157.07 % | 145.93 % | 157.07 / 145.93 ✓ |
| LTB utilisation | 22.70 % | 22.70 % | 22.70 / 22.70 ✓ |

So this is confirmed independently on two platforms.

One useful detail: in my *original* report I used a slightly different bridge (carriageway 10.5 m → 5 girders, no project location) and there the shear difference went the **other way** (+15° ≈ 59 % vs −15° ≈ 41 %), while flexure/fatigue were still higher for +15°. The fact that the *direction* of the shear change flips between geometries — but the results are sign-dependent in every case — tells us this is not a fixed sign bias in a correction factor; it is the mirrored skew changing how the load is distributed among girders, so a different girder governs. That is consistent with a load-placement / element-mapping problem for oblique meshes rather than a simple wrong constant.

Also note LTB is identical in both of our setups: it is a self-weight-governed check, while flexure/shear/fatigue (live-load driven) are the ones that change — further support for the load path being the culprit.

Happy to share my input/output dictionaries (both ±15° cases) if useful for tracing the element lookup; I can also run any additional skew values you suggest.
