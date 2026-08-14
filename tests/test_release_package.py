from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts" / "build_release.py"
CANONICAL_SKILL = ROOT / ".agents" / "skills" / "paper-deep-analysis"
CLAUDE_SKILL = ROOT / ".claude" / "skills" / "paper-deep-analysis"


def build(output_dir: Path) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT), "--output-dir", str(output_dir)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return json.loads(completed.stdout)


def test_claude_project_entry_points_to_canonical_skill() -> None:
    assert CLAUDE_SKILL.is_symlink()
    assert CLAUDE_SKILL.resolve() == CANONICAL_SKILL.resolve()
    assert (CLAUDE_SKILL / "SKILL.md").is_file()


def test_release_package_contains_only_installable_skill_files(tmp_path: Path) -> None:
    result = build(tmp_path)
    archive_path = Path(str(result["archive"]))
    manifest = json.loads((tmp_path / "release-manifest.json").read_text(encoding="utf-8"))
    with zipfile.ZipFile(archive_path) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
    assert "paper-deep-analysis/SKILL.md" in names
    assert "paper-deep-analysis/LICENSE" in names
    assert "paper-deep-analysis/agents/openai.yaml" in names
    assert not any("__pycache__" in name or name.endswith(".pyc") for name in names)
    assert not any(name.startswith("paper-deep-analysis/tests/") for name in names)
    assert manifest["compatible_clients"] == ["OpenAI Codex", "Claude Code"]
    assert manifest["file_count"] == len(names)
    assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == manifest["archive_sha256"]


def test_release_archive_is_deterministic(tmp_path: Path) -> None:
    first = build(tmp_path / "first")
    second = build(tmp_path / "second")
    assert Path(str(first["archive"])).read_bytes() == Path(str(second["archive"])).read_bytes()
