# Proof — #316: Longitudinal shear VL mixes the plastic neutral axis with the elastic inertia

**Issue:** https://github.com/Nidhikhare12/OsdagBridge/issues/316  

**Severity:** S2 (VL understated 29 %; deck transverse reinforcement requirement 29 % low) · **Tier:** T1 (two fresh processes, fix proven)
**Environment:** OsdagBridge `dev` @ `d74f56d` · macOS 13.6 · conda env `osdagbridge-env` · tested 2026-11-24

## Reproduce
```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate osdagbridge-env
cd osdagbridge-testing-report
P=proofs/316_longitudinal_shear_plastic_vs_elastic_na
python $P/scripts/probe_stud_vl_neutral_axis.py $P/inputs/H_s20_params.json          # as shipped
python $P/scripts/probe_stud_vl_neutral_axis.py $P/inputs/H_s20_params.json --fix    # fix proof
```

## Key result
`VL = V·(Aec·Y)/Ic` (`irc22_2015.py:1776`) takes `Y = xu − t_eff/2` about the **plastic** neutral axis (`:1766`) while `Ic` is the **elastic** short-term composite inertia. It also uses `n = Es/Ecm = 6.061` (`:1757`) instead of the IRC 22 Cl. 604.3 floor of 7.5 that `Ic` was built with.

| Quantity (span 20 m, cw 7.5 m) | As shipped | Elastic NA, n = 7.5 | Change |
|---|---|---|---|
| `VL_N_per_mm` | **116.913** | 164.136 | +40.4 % |
| Stud spacing `sl1` (ULS) | 1631.35 mm | 1162.00 mm | −28.8 % |
| Stud spacing provided | 303.81 mm | 303.81 mm | unchanged |
| Deck transverse shear VL | 116.913 kN/m | 164.136 kN/m | +40.4 % |
| **`Ast_required_cm2_per_m`** | **0.585** | **0.821** | **+40.4 %** |
| `ur_composite_trans_shear` | 0.117 | 0.1643 | +40.4 % |

Hand check: transformed slab area = 2100 × 250 / 7.5 = 70 000 mm²; elastic NA = (70 000×125 + 19 584×810)/89 584 = 274.75 mm, which matches the program's own `y_top_comp_mm` = 274.748; ȳ = 149.748 mm;
VL = 183 500 × 70 000 × 149.748 / 11 719 028 660 = **164.14 N/mm** — matches the patched run.

## Evidence
| File | What it shows |
|---|---|
| `logs/probe_stud_vl_neutral_axis.log` | Two fresh runs as shipped (identical) plus the fix proof, with the deck transverse-shear outputs |
| `scripts/probe_stud_vl_neutral_axis.py` | Probe and the elastic-NA correction |
| `inputs/H_s20_params.json` | Exact input |

## Root cause
`irc22_2015.py:1757` and `:1766`, used with the elastic `Ic` at `:1776`. `VL` feeds the stud spacing and, per `designer.py:1950-1951`, the deck transverse-shear check of Cl. 606.10 that sizes the slab reinforcement.

## Notes
No check flips in the tested case: the provided stud spacing is governed by the full-shear-connection criterion (303.81 mm) rather than `sl1`, and the provided transverse steel (11.38 cm²/m) is set by other minima. The finding is that a reported design quantity — the required transverse reinforcement — is 29 % low, and that `sl1` would govern on a girder with higher shear.

The issue text as posted is in `ISSUE_316.md`.
