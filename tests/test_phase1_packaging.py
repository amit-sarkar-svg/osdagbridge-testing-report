import os, subprocess, sys
from pathlib import Path
import yaml

CLONE = Path("/Users/macbook/Projects/OsdagBridge")

def test_examples_parse_and_validate():
    from osdagbridge.core.utils.osi_validator import validate_osi_inputs
    from osdagbridge.core.utils.common import KEY_SPAN, KEY_CARRIAGEWAY_WIDTH, KEY_SKEW_ANGLE
    base = CLONE / "examples/plate_girder"
    # example_basic: placeholder keys, no real dotted geometry keys, but loader validates vacuously
    d = yaml.safe_load((base / "example_basic.yaml").read_text())
    assert isinstance(d, dict) and "project" in d
    assert not ({KEY_SPAN, KEY_CARRIAGEWAY_WIDTH, KEY_SKEW_ANGLE} & set(d.keys()))
    r = validate_osi_inputs(d)
    assert r.is_valid is True and r.errors == []
    # verification placeholders are empty -> invalid
    for name in ("verification_case_01.yaml", "verification_case_02.yaml"):
        d2 = yaml.safe_load((base / name).read_text())
        r2 = validate_osi_inputs(d2)
        assert r2.is_valid is False
        assert any("valid input dictionary" in e.lower() for e in r2.errors)

def test_cli_stub_ignores_args():
    # documented commands do not behave as README states; CLI prints stub and ignores args
    p = subprocess.run(["osdagbridge-cli", "--help"], capture_output=True, text=True, timeout=30)
    out = (p.stdout + p.stderr)
    assert "CLI (stub)" in out
    p2 = subprocess.run(["osdagbridge-cli", "analyze", "project.yaml"], capture_output=True, text=True, timeout=30)
    out2 = (p2.stdout + p2.stderr)
    assert "CLI (stub)" in out2

def test_pyproject_missing_key_runtime_deps():
    text = (CLONE / "pyproject.toml").read_text()
    # pyproject declares a deps list that omits PySide6/numpy/osdag_core/yaml despite source imports/usage
    assert "PySide6" not in text.split("dependencies = [",1)[1].split("]",1)[0]
    assert "numpy" not in text.split("dependencies = [",1)[1].split("]",1)[0]
    assert "osdag_core" not in text
    assert "PyYAML" not in text and "pyyaml" not in text.lower().split("dependencies = [",1)[1].split("]",1)[0]

def test_osdag_core_declares_bogus_sqlite_dep():
    import importlib.metadata as m
    reqs = m.distribution("osdag_core").metadata.get_all("Requires-Dist") or []
    assert any(r.strip().startswith("sqlite") for r in reqs)
