import json
import os
from pathlib import Path
import subprocess
import sys
import pytest


def cli(*args):
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).parents[1] / "src"))
    return subprocess.run([sys.executable, "-m", "moleculebench.cli", *map(str, args)],
                          env=env, capture_output=True, text=True)


def test_default_configuration():
    result = cli("config")
    assert result.returncode == 0
    assert json.loads(result.stdout)["scan_basis"] == "sto-3g"


@pytest.mark.parametrize("raw", ['[]', '{"points":true}', '{"tolerance":NaN}', '{"bad":1}', '{'])
def test_bad_configuration_no_output(tmp_path, raw):
    config = tmp_path / "input.json"
    config.write_text(raw)
    output = tmp_path / "result"
    result = cli("run", "--config", config, "--output", output)
    assert result.returncode == 2
    assert "MoleculeBench:" in result.stderr
    assert not output.exists()


def test_existing_output_preserved(tmp_path):
    marker = tmp_path / "user.txt"
    marker.write_text("retain this")
    assert cli("run", "--output", tmp_path).returncode == 2
    assert marker.read_text() == "retain this"


def test_small_report_is_real_and_portable(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"points": 3}))
    output = tmp_path / "report"
    result = cli("run", "--config", config, "--output", output)
    assert result.returncode == 0, result.stderr
    data = json.loads((output / "results.json").read_text())
    assert len(data["scan"]) == 3 and len(data["basis_comparison"]) == 4
    assert data["summary"]["max_dense_fci_delta_hartree"] < 1e-7
    html = (output / "index.html").read_text()
    assert "__RESULT_DATA__" not in html
    assert 'id="results"' in html
    assert 'src="http' not in html and 'href="https://fonts' not in html
    assert (output / "scan.csv").read_text().count("\n") == 4
    assert (output / "energy-curves.png").stat().st_size > 1000


@pytest.mark.parametrize("raw", [
    *[json.dumps({field: 10**400}) for field in
      ("start_angstrom", "stop_angstrom", "comparison_angstrom", "tolerance")],
    '{"points":3,"points":4}',
    ' '*16384 + '{}',
    '['*1200 + '0' + ']'*1200,
])
def test_invalid_config_is_bounded_normal_error(tmp_path, raw):
    config = tmp_path / "invalid.json"
    config.write_text(raw)
    output = tmp_path / "result"
    result = cli("run", "--config", config, "--output", output)
    assert result.returncode == 2
    assert result.stderr.startswith("MoleculeBench:")
    assert "Traceback" not in result.stderr
    assert not output.exists()
