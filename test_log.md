# Test Log

| ID | Date | Area | Parameters (exact) | Expected | Actual | Result | Evidence | Issue |
|----|------|------|--------------------|----------|--------|--------|----------|-------|
| PYT-01 | 2026-11-15 | validator-steel | validate_material_inputs: density 49.9/50.0/120.0/120.1, fy 99.9/100.0/1200.0/1200.1, fu 99.9/1500.1, E 99.9/300.1, G 29.9/120.1, poisson -0.01/0.51, thermal 0.9/30.1 (tests/test_validator_limits.py) | outside -> corrected to limit; inside -> None | outside corrected to limit, inside None (7 params) | PASS | tests/test_validator_limits.py, pytest output | |
| PYT-02 | 2026-11-15 | validator-deck | validate_material_inputs: density 17.9/28.1, fck 9.9/80.1, fctm 0.49/6.1, Ecm 14.9/50.1, thermal 4.9/15.1 (tests/test_validator_limits.py) | outside -> corrected to limit; inside -> None | outside corrected to limit, inside None (5 params) | PASS | tests/test_validator_limits.py | |
| PYT-03 | 2026-11-15 | validator-geometry | span 19.9/45.1 -> corrected 20.0/45.0; carriageway 4.25/23.6 pass, 23.7 -> 23.6; median Yes + 5.0 -> 7.5; skew -15.1/15.1 -> corrected | as stated | as stated | PASS | tests/test_validator_limits.py | |
| PYT-04 | 2026-11-15 | validator-NaN | span = float('nan') fed to validate_basic_inputs | error returned (NaN rejected) | None returned (NaN accepted as valid) | CANDIDATE BUG | pytest failure, root cause validator.py _to_float L1094-1098 + comparisons L32-35 | duplicate of #88 (adds exact root cause) |
| PYT-05 | 2026-11-15 | osi-round-trip | default dict -> yaml.dump -> yaml.safe_load -> dict equality + validate_osi_inputs | equal + valid | equal + valid | PASS | tests/test_osi_round_trip.py | |
| F3-96 | 2026-11-15 | osi-material-bypass | validate_osi_inputs({material.girder.fy: 99999.0, material.girder.density: 5.0, material.deck.fck: -3.0}); same values through validate_material_inputs | OSI loader rejects out-of-range material values (lock-step with Material dialog) | is_valid=True, errors=[] from loader; validate_material_inputs rejects all three (1200.0/50.0/10.0) | BUG (filed) | evidence/analyze/osi_material_bypass.txt | #96 |

