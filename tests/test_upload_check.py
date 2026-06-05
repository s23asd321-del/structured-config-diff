from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "check_upload_ready.py"


def _load_upload_check_module():
    spec = importlib.util.spec_from_file_location("check_upload_ready", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _create_required_files(root: Path, required_files: tuple[str, ...]) -> None:
    for relative in required_files:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder\n", encoding="utf-8")


def test_upload_check_passes_for_minimal_clean_tree(tmp_path):
    module = _load_upload_check_module()
    _create_required_files(tmp_path, module.REQUIRED_FILES)

    assert module.run_checks(tmp_path) == []


def test_upload_check_flags_generated_artifacts(tmp_path):
    module = _load_upload_check_module()
    _create_required_files(tmp_path, module.REQUIRED_FILES)
    (tmp_path / ".venv").mkdir()

    failures = module.run_checks(tmp_path)

    assert "generated artifact should not be uploaded: .venv" in failures


def test_upload_check_flags_nested_pycache(tmp_path):
    module = _load_upload_check_module()
    _create_required_files(tmp_path, module.REQUIRED_FILES)
    (tmp_path / "scripts" / "__pycache__").mkdir(parents=True)

    failures = module.run_checks(tmp_path)

    assert "generated artifact should not be uploaded: scripts/__pycache__" in failures
