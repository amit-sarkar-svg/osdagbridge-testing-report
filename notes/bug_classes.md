# Bug Classes — OsdagBridge Issue Classification (89 issues, issue_raw.json)

## custom_value_ignored
- **Pattern**: user-settable value stored but never used in design/analysis; silently falls back to default
- **Issue numbers**: #43, #41, #20, #19, #115, #103
- **Root-cause code pattern**: `.get(KEY_`, `setdefault`, `or DEFAULT`

## unit_mixup
- **Pattern**: quantity unit confusion (GPa vs MPa, mm vs m, kN vs N); same quantity used in two different units
- **Issue numbers**: #148, #85, #82
- **Root-cause code pattern**: `1000|1e3|1e-3|1e6|/ 1000|\* 1000|mm|kN|kNm|MPa|GPa` near property names

## stale_overwritten_state
- **Pattern**: state persists across consecutive design runs without reset, or overwritten silently
- **Issue numbers**: #125, #111, #113, #90, #89, #73
- **Root-cause code pattern**: class attributes set in `design()` but missing from `__init__` or `reset()`; module-level caches

## wrong_aggregation
- **Pattern**: incorrect per-girder or overall aggregation (off-by-one, first-element-only use of lists)
- **Issue numbers**: #151, #112, #109, #56
- **Root-cause code pattern**: `sum(`, `max(`, `min(`, `mean(`, `girders[0]`, `girders[-1]`, `range(n)`, `n-1`

## ui_not_updated
- **Pattern**: widget changed programmatically without the signal that updates the dict, or dict updated without the widget, in lock/unlock/reset/load flows
- **Issue numbers**: #98, #110, #67, #73, #72
- **Root-cause code pattern**: `unlock(`, `lock(`, `set_input_dictionary`, `populate_from_dict`

## validation_gap
- **Pattern**: validator accepts invalid values (NaN, inf, out-of-range), or skips validation for certain keys
- **Issue numbers**: #134, #133, #69, #66, #88
- **Root-cause code pattern**: `validate_osi_inputs`, `validate_additional_inputs`, `_to_float`, `safe_load`

## report_mismatch
- **Pattern**: report output differs from design output dock or computed values; tables repeat controlling girder
- **Issue numbers**: #151, #147, #120, #117, #116
- **Root-cause code pattern**: `pylatex`, `pdflatex`, `generate_pdf`, `Report(`

## crash_performance
- **Pattern**: crashes or very slow design runs (>10 min)
- **Issue numbers**: #135, #133, #122, #118, #71
- **Root-cause code pattern**: `math domain error`, `ValueError`, `Timeout`, `> 10 min`

## file_io_robustness
- **Pattern**: save/load edge cases, yaml unsafe tags, path handling, missing extension enforcement
- **Issue numbers**: #131, #127, #128, #88, #96
- **Root-cause code pattern**: `yaml.dump`, `yaml.safe_load`, `yaml.full_load`, `pickle`, `QFileDialog`

## installation_env
- **Pattern**: dependency, env, or package configuration issues; missing Requires-Dist or bogus packages
- **Issue numbers**: #126, #100, #105, #99, #97
- **Root-cause code pattern**: `pyproject.toml`, `requirements.txt`, `environment.yml`, `pydantic`, `sqlite`