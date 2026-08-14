#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

from release_audit import LOCAL_PATH_PATTERNS, MAX_PUBLIC_FILE_BYTES, SECRET_PATTERNS


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "paper-deep-analysis"
SKILL_ROOT = ROOT / ".agents" / "skills" / SKILL_NAME
ROOT_LICENSE = ROOT / "LICENSE"
ALLOWED_SUFFIXES = {".json", ".md", ".py", ".yaml", ".yml"}
IGNORED_PARTS = {"__pycache__", ".DS_Store"}
VERSION_RE = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def project_version() -> str:
    match = VERSION_RE.search((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    if not match:
        raise ValueError("pyproject.toml does not contain a quoted project version")
    return match.group(1)


def runtime_files() -> list[tuple[Path, str, bytes]]:
    required = {
        "SKILL.md",
        "agents/openai.yaml",
        "assets/analysis-template.json",
        "assets/run-template.json",
    }
    files: list[tuple[Path, str, bytes]] = []
    for path in sorted(SKILL_ROOT.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(SKILL_ROOT)
        if any(part in IGNORED_PARTS for part in relative.parts) or path.suffix == ".pyc":
            continue
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            raise ValueError(f"unexpected runtime file type: {relative.as_posix()}")
        data = path.read_bytes()
        if len(data) > MAX_PUBLIC_FILE_BYTES:
            raise ValueError(f"runtime file exceeds the public size limit: {relative.as_posix()}")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"runtime file is not UTF-8 text: {relative.as_posix()}") from exc
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                raise ValueError(f"runtime file contains a possible {label}: {relative.as_posix()}")
        if relative.as_posix() != "scripts/paperlib/common.py" and any(pattern.search(text) for pattern in LOCAL_PATH_PATTERNS):
            raise ValueError(f"runtime file contains a local path or file URL: {relative.as_posix()}")
        if path.suffix.lower() == ".json":
            json.loads(text)
        files.append((path, relative.as_posix(), data))
    found = {relative for _, relative, _ in files}
    missing = sorted(required - found)
    if missing:
        raise ValueError(f"release source is missing required files: {missing}")
    license_data = ROOT_LICENSE.read_bytes()
    files.append((ROOT_LICENSE, "LICENSE", license_data))
    return sorted(files, key=lambda item: item[1])


def write_archive(path: Path, files: list[tuple[Path, str, bytes]]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for _, relative, data in files:
            info = zipfile.ZipInfo(f"{SKILL_NAME}/{relative}", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if relative.endswith(".py") else 0o644
            info.external_attr = mode << 16
            archive.writestr(info, data)


def verify_archive(path: Path, files: list[tuple[Path, str, bytes]]) -> None:
    expected = {f"{SKILL_NAME}/{relative}": sha256_bytes(data) for _, relative, data in files}
    with zipfile.ZipFile(path) as archive:
        actual_names = sorted(name for name in archive.namelist() if not name.endswith("/"))
        if actual_names != sorted(expected):
            raise ValueError("archive file list does not match the runtime source")
        for name, digest in expected.items():
            if sha256_bytes(archive.read(name)) != digest:
                raise ValueError(f"archive checksum mismatch: {name}")


def build(output_dir: Path, *, force: bool = False) -> dict[str, object]:
    version = project_version()
    archive_name = f"{SKILL_NAME}-v{version}.zip"
    package_dir = output_dir / SKILL_NAME
    archive_path = output_dir / archive_name
    manifest_path = output_dir / "release-manifest.json"
    checksum_path = output_dir / "SHA256SUMS"
    targets = (package_dir, archive_path, manifest_path, checksum_path)
    existing = [path for path in targets if path.exists() or path.is_symlink()]
    if existing and not force:
        names = ", ".join(path.name for path in existing)
        raise FileExistsError(f"release output already exists ({names}); rerun with --force")

    output_dir.mkdir(parents=True, exist_ok=True)
    files = runtime_files()
    with tempfile.TemporaryDirectory(prefix="paper-deep-analysis-release-", dir=output_dir) as temporary:
        stage = Path(temporary)
        staged_package = stage / SKILL_NAME
        for _, relative, data in files:
            destination = staged_package / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        staged_archive = stage / archive_name
        write_archive(staged_archive, files)
        verify_archive(staged_archive, files)

        archive_digest = sha256_bytes(staged_archive.read_bytes())
        manifest = {
            "schema_version": "1.0",
            "name": SKILL_NAME,
            "version": version,
            "format": "Agent Skills",
            "compatible_clients": ["OpenAI Codex", "Claude Code"],
            "archive": archive_name,
            "archive_sha256": archive_digest,
            "file_count": len(files),
            "files": [
                {"path": relative, "sha256": sha256_bytes(data), "bytes": len(data)}
                for _, relative, data in files
            ],
        }
        (stage / "release-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (stage / "SHA256SUMS").write_text(f"{archive_digest}  {archive_name}\n", encoding="utf-8")

        if force:
            for path in targets:
                if path.is_dir() and not path.is_symlink():
                    shutil.rmtree(path)
                elif path.exists() or path.is_symlink():
                    path.unlink()
        shutil.move(str(staged_package), package_dir)
        shutil.move(str(staged_archive), archive_path)
        shutil.move(str(stage / "release-manifest.json"), manifest_path)
        shutil.move(str(stage / "SHA256SUMS"), checksum_path)

    return {
        "status": "pass",
        "package_dir": str(package_dir),
        "archive": str(archive_path),
        "archive_sha256": manifest["archive_sha256"],
        "manifest": str(manifest_path),
        "file_count": manifest["file_count"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic, runtime-only Agent Skill release package.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--force", action="store_true", help="Replace only the named release outputs in the output directory.")
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir.resolve(), force=args.force), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
