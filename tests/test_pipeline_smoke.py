import json
from pathlib import Path
import subprocess
import sys

def test_smoke_analyze_and_validate(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]
    out_dir = tmp_path / "out"
    cmd = [sys.executable, "-m", "soc_agentic_forensics", "analyze", str(repo/"samples"/"case01"), "--out", str(out_dir), "--schema-dir", str(repo/"schemas")]
    r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout

    report = json.loads((out_dir/"report.json").read_text(encoding="utf-8"))
    assert report["hostname"] == "WS-123"

    cmd2 = [sys.executable, "-m", "soc_agentic_forensics", "validate", str(out_dir/"report.json"), "--schema-dir", str(repo/"schemas")]
    r2 = subprocess.run(cmd2, cwd=repo, capture_output=True, text=True)
    assert r2.returncode == 0, r2.stderr + r2.stdout
