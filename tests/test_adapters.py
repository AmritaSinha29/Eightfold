"""Tests for source adapters.

Each test class covers one adapter. Tests marked pytest.skip are stubs —
they document intent and will be filled in during implementation.
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.adapters.ats_json_adapter import ATSJsonAdapter
from src.adapters.csv_adapter import CSVAdapter
from src.adapters.github_adapter import GitHubAdapter
from src.adapters.notes_adapter import NotesAdapter
from src.adapters.resume_adapter import ResumeAdapter
from src.models.raw_record import RawRecord


class TestCSVAdapter:
    """Tests for CSVAdapter."""

    def test_can_handle_csv_extension(self):
        """CSVAdapter.can_handle should return True for .csv paths."""
        # TODO: adapter = CSVAdapter()
        # TODO: assert adapter.can_handle("recruiter.csv") is True
        # TODO: assert adapter.can_handle("data.json") is False
        pytest.skip("Not yet implemented")

    def test_returns_empty_on_missing_file(self):
        """CSVAdapter.load should return [] when the file does not exist."""
        # TODO: adapter = CSVAdapter()
        # TODO: result = adapter.load("/nonexistent/path.csv")
        # TODO: assert result == []
        pytest.skip("Not yet implemented")

    def test_parses_standard_columns(self, tmp_path: Path):
        """CSVAdapter should map name/email/phone/company/title to RawRecord fields."""
        # TODO: Write a 1-row CSV to tmp_path / "test.csv"
        # TODO: result = CSVAdapter().load(str(tmp_path / "test.csv"))
        # TODO: assert len(result) == 1
        # TODO: assert result[0].full_name == "Alice Johnson"
        # TODO: assert "alice@example.com" in result[0].emails
        pytest.skip("Not yet implemented")

    def test_handles_extra_columns(self, tmp_path: Path):
        """Unknown CSV columns should be stored in RawRecord.extra."""
        # TODO: CSV with extra "linkedin_url" column
        # TODO: assert "linkedin_url" in result[0].extra
        pytest.skip("Not yet implemented")

    def test_skips_empty_rows(self, tmp_path: Path):
        """Blank rows in the CSV should produce no RawRecord."""
        pytest.skip("Not yet implemented")

    def test_case_insensitive_headers(self, tmp_path: Path):
        """Header casing should not affect field mapping."""
        # TODO: CSV with headers "NAME", "EMAIL" etc.
        # TODO: assert result[0].full_name is not None
        pytest.skip("Not yet implemented")


class TestATSJsonAdapter:
    """Tests for ATSJsonAdapter."""

    def test_returns_empty_on_missing_file(self):
        """ATSJsonAdapter.load should return [] for a missing file."""
        pytest.skip("Not yet implemented")

    def test_returns_empty_on_invalid_json(self, tmp_path: Path):
        """ATSJsonAdapter.load should return [] for malformed JSON."""
        # TODO: Write "not valid json" to a .json file
        # TODO: assert ATSJsonAdapter().load(path) == []
        pytest.skip("Not yet implemented")

    def test_applies_default_field_map(self, tmp_path: Path):
        """ATSJsonAdapter should remap ATS field names using the default map."""
        # TODO: Write ATS JSON with candidate_name, primary_email, etc.
        # TODO: assert result[0].full_name == "Alice Johnson"
        pytest.skip("Not yet implemented")

    def test_handles_array_root(self, tmp_path: Path):
        """A JSON array at root should produce one RawRecord per element."""
        pytest.skip("Not yet implemented")

    def test_load_field_map_validates_format(self, tmp_path: Path):
        """load_field_map should raise ValueError for non-string values in the map."""
        pytest.skip("Not yet implemented")


class TestGitHubAdapter:
    """Tests for GitHubAdapter."""

    def test_can_handle_github_profile_url(self):
        """GitHubAdapter.can_handle should return True for github.com profile URLs."""
        # TODO: assert GitHubAdapter().can_handle("https://github.com/octocat") is True
        pytest.skip("Not yet implemented")

    def test_rejects_repo_url(self):
        """GitHubAdapter.can_handle should return False for repo URLs."""
        # TODO: assert GitHubAdapter().can_handle("https://github.com/user/repo") is False
        pytest.skip("Not yet implemented")

    def test_returns_empty_on_404(self):
        """GitHubAdapter.load should return [] when the profile does not exist."""
        pytest.skip("Not yet implemented")

    def test_extracts_languages_from_repos(self):
        """_extract_languages should return unique RawSkill per language."""
        pytest.skip("Not yet implemented")


class TestNotesAdapter:
    """Tests for NotesAdapter."""

    def test_can_handle_txt_extension(self):
        """NotesAdapter.can_handle should return True for .txt paths."""
        pytest.skip("Not yet implemented")

    def test_returns_empty_on_missing_file(self):
        """NotesAdapter.load should return [] for a missing file."""
        pytest.skip("Not yet implemented")

    def test_extracts_email_from_text(self, tmp_path: Path):
        """NotesAdapter should find email addresses in free text."""
        # TODO: Write "Email: alice@example.com" to a .txt file
        # TODO: assert "alice@example.com" in result[0].emails
        pytest.skip("Not yet implemented")

    def test_extracts_name_from_label(self, tmp_path: Path):
        """NotesAdapter should extract name from 'Candidate: ...' prefix."""
        pytest.skip("Not yet implemented")

    def test_returns_empty_on_blank_file(self, tmp_path: Path):
        """An all-whitespace notes file should return []."""
        pytest.skip("Not yet implemented")


class TestResumeAdapter:
    """Tests for ResumeAdapter."""

    def test_can_handle_pdf_and_docx(self):
        """ResumeAdapter.can_handle should accept .pdf and .docx."""
        pytest.skip("Not yet implemented")

    def test_returns_empty_on_missing_file(self):
        """ResumeAdapter.load should return [] for a missing file."""
        pytest.skip("Not yet implemented")
