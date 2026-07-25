"""v3.2.1 release metadata and production-incident correction regressions."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUI = (ROOT / "app" / "gui.py").read_text(encoding="utf-8")
CONTROLLER = (ROOT / "app" / "controller.py").read_text(encoding="utf-8")
ADAPTER = (ROOT / "app" / "ib_adapter.py").read_text(encoding="utf-8")
STRATEGY = (ROOT / "app" / "strategy.py").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
CHANGELOG = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
PYPROJECT = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
BUILD = (ROOT / "scripts" / "build_windows.ps1").read_text(encoding="utf-8")
SECURITY = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
DOCS_INDEX = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
LEGACY_INDEX = (ROOT / "docs" / "legacy" / "README.md").read_text(encoding="utf-8")
CURRENT_NOTE = ROOT / "docs" / "V3_2_1_INCIDENT_GAP_CORRECTIONS.md"
ARCHIVED_V320_NOTE = ROOT / "docs" / "legacy" / "V3_2_0_EUR_SMART_AND_RECONNECT.md"


def test_v321_release_metadata_is_consistent() -> None:
    assert "BouncyBot - IBKR Portable Trading Bot v3.2.1" in GUI
    assert "This is synthetic v3.2.1 paper-trading example data." in GUI
    assert "**Current release: v3.2.1**" in README
    assert 'version = "3.2.1"' in PYPROJECT
    assert '$version = "3.2.1"' in BUILD
    assert "## v3.2.1" in CHANGELOG
    assert "current repository version, v3.2.1" in SECURITY
    assert "current v3.2.1 behavior" in DOCS_INDEX


def test_v321_release_note_is_current_and_v320_is_archived() -> None:
    assert CURRENT_NOTE.is_file()
    assert ARCHIVED_V320_NOTE.is_file()
    assert not (ROOT / "docs" / "V3_2_0_EUR_SMART_AND_RECONNECT.md").exists()
    assert "V3_2_1_INCIDENT_GAP_CORRECTIONS.md" in README
    assert "V3_2_1_INCIDENT_GAP_CORRECTIONS.md" in DOCS_INDEX
    assert "V3_2_0_EUR_SMART_AND_RECONNECT.md" in LEGACY_INDEX


def test_v321_source_contains_all_three_incident_gap_corrections() -> None:
    assert '_PRIMARY_EXCHANGE_CONTINUOUS_SESSIONS' in ADAPTER
    assert '"LSE": ("Europe/London", dt.time(8, 0), dt.time(16, 30))' in ADAPTER
    assert '"LSEETF": ("Europe/London", dt.time(8, 0), dt.time(16, 30))' in ADAPTER
    assert "_apply_primary_exchange_continuous_session" in ADAPTER
    assert "_close_cached_rth_status_at_boundary" in ADAPTER
    assert "BUY_PREFLIGHT_AUDIT_THROTTLE_SECONDS = 60.0" in CONTROLLER
    assert "buy_preflight_block|" in CONTROLLER
    assert "rollback_preflight_blocked_order" in STRATEGY
    assert 'next_cycle.buy_status = "PreflightBlocked"' in STRATEGY


def test_v321_release_note_documents_scope_and_compatibility() -> None:
    text = CURRENT_NOTE.read_text(encoding="utf-8")
    assert "08:00-16:30" in text
    assert "LSEETF" in text
    assert "PreflightBlocked" in text
    assert "one audit event per 60 seconds" in text
    assert "adds no SQLite table, column, or index" in text
    assert "paper-account" in text


def test_v321_has_no_strict_known_gap_sentinel_file() -> None:
    assert not (ROOT / "tests" / "test_known_incident_gaps.py").exists()
    replacement = ROOT / "tests" / "test_v321_incident_gap_fixes.py"
    assert replacement.is_file()
    assert "pytest.mark.xfail" not in replacement.read_text(encoding="utf-8")
