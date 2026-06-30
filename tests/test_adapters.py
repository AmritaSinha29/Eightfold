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
        adapter = CSVAdapter()
        assert adapter.can_handle("recruiter.csv") is True
        assert adapter.can_handle("data.json") is False

    def test_returns_empty_on_missing_file(self):
        """CSVAdapter.load should return [] when the file does not exist."""
        adapter = CSVAdapter()
        result = adapter.load("/nonexistent/path.csv")
        assert result == []

    def test_parses_standard_columns(self, tmp_path: Path):
        """CSVAdapter should map name/email/phone/company/title to RawRecord fields."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(
            "name,email,phone,current_company,title\n"
            "Alice Johnson,alice@example.com,(415) 555-0101,Acme Corp,Engineer\n"
        )
        result = CSVAdapter().load(str(csv_file))
        assert len(result) == 1
        assert result[0].full_name == "Alice Johnson"
        assert "alice@example.com" in result[0].emails

    def test_handles_extra_columns(self, tmp_path: Path):
        """Unknown CSV columns should be stored in RawRecord.extra."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(
            "name,email,linkedin_url\n"
            "Alice,alice@x.com,https://linkedin.com/in/alice\n"
        )
        result = CSVAdapter().load(str(csv_file))
        assert len(result) == 1
        assert "linkedin_url" in result[0].extra

    def test_skips_empty_rows(self, tmp_path: Path):
        """Blank rows in the CSV should produce no RawRecord."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,email\nAlice,alice@x.com\n,\n\n")
        result = CSVAdapter().load(str(csv_file))
        assert len(result) == 1

    def test_case_insensitive_headers(self, tmp_path: Path):
        """Header casing should not affect field mapping."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("NAME,EMAIL\nAlice Johnson,alice@example.com\n")
        result = CSVAdapter().load(str(csv_file))
        assert len(result) == 1
        assert result[0].full_name == "Alice Johnson"


class TestATSJsonAdapter:
    """Tests for ATSJsonAdapter."""

    def test_returns_empty_on_missing_file(self):
        """ATSJsonAdapter.load should return [] for a missing file."""
        assert ATSJsonAdapter().load("/nonexistent/file.json") == []

    def test_returns_empty_on_invalid_json(self, tmp_path: Path):
        """ATSJsonAdapter.load should return [] for malformed JSON."""
        path = tmp_path / "bad.json"
        path.write_text("not valid json")
        assert ATSJsonAdapter().load(str(path)) == []

    def test_applies_default_field_map(self, tmp_path: Path):
        """ATSJsonAdapter should remap ATS field names using the default map."""
        data = {"candidate_name": "Alice Johnson", "primary_email": "alice@example.com"}
        path = tmp_path / "ats.json"
        path.write_text(json.dumps(data))
        result = ATSJsonAdapter().load(str(path))
        assert len(result) == 1
        assert result[0].full_name == "Alice Johnson"
        assert "alice@example.com" in result[0].emails

    def test_handles_array_root(self, tmp_path: Path):
        """A JSON array at root should produce one RawRecord per element."""
        data = [{"candidate_name": "Alice"}, {"candidate_name": "Bob"}]
        path = tmp_path / "ats.json"
        path.write_text(json.dumps(data))
        result = ATSJsonAdapter().load(str(path))
        assert len(result) == 2

    def test_load_field_map_validates_format(self, tmp_path: Path):
        """load_field_map should raise ValueError for non-string values in the map."""
        map_path = tmp_path / "bad_map.json"
        map_path.write_text(json.dumps({"key": 123}))
        with pytest.raises(ValueError):
            ATSJsonAdapter.load_field_map(str(map_path))


class TestGitHubAdapter:
    """Tests for GitHubAdapter."""

    def test_can_handle_github_profile_url(self):
        """GitHubAdapter.can_handle should return True for github.com profile URLs."""
        assert GitHubAdapter().can_handle("https://github.com/octocat") is True

    def test_rejects_repo_url(self):
        """GitHubAdapter.can_handle should return False for repo URLs."""
        assert GitHubAdapter().can_handle("https://github.com/user/repo") is False

    def test_returns_empty_on_404(self):
        """GitHubAdapter.load should return [] when the profile does not exist."""
        adapter = GitHubAdapter()
        with patch.object(adapter, "_fetch_user", return_value={}):
            result = adapter.load("https://github.com/nonexistent-user-xyz-9999")
        assert result == []

    def test_extracts_languages_from_repos(self):
        """_extract_languages should return unique RawSkill per language."""
        repos = [
            {"language": "Python"},
            {"language": "JavaScript"},
            {"language": "Python"},
        ]
        skills = GitHubAdapter()._extract_languages(repos)
        names = [s.name for s in skills]
        assert "Python" in names
        assert "JavaScript" in names
        assert names.count("Python") == 1


class TestNotesAdapter:
    """Tests for NotesAdapter."""

    def test_can_handle_txt_extension(self):
        """NotesAdapter.can_handle should return True for .txt paths."""
        assert NotesAdapter().can_handle("notes.txt") is True
        assert NotesAdapter().can_handle("data.csv") is False

    def test_returns_empty_on_missing_file(self):
        """NotesAdapter.load should return [] for a missing file."""
        assert NotesAdapter().load("/nonexistent/notes.txt") == []

    def test_extracts_email_from_text(self, tmp_path: Path):
        """NotesAdapter should find email addresses in free text."""
        f = tmp_path / "notes.txt"
        f.write_text("Email: alice@example.com\nSome notes about this candidate.")
        result = NotesAdapter().load(str(f))
        assert len(result) == 1
        assert "alice@example.com" in result[0].emails

    def test_extracts_name_from_label(self, tmp_path: Path):
        """NotesAdapter should extract name from 'Candidate: ...' prefix."""
        f = tmp_path / "notes.txt"
        f.write_text("Candidate: Alice Johnson\nEmail: alice@example.com")
        result = NotesAdapter().load(str(f))
        assert len(result) == 1
        assert result[0].full_name == "Alice Johnson"

    def test_returns_empty_on_blank_file(self, tmp_path: Path):
        """An all-whitespace notes file should return []."""
        f = tmp_path / "notes.txt"
        f.write_text("   \n\n   ")
        result = NotesAdapter().load(str(f))
        assert result == []


class TestResumeAdapter:
    """Tests for ResumeAdapter."""

    def test_can_handle_pdf_and_docx(self):
        """ResumeAdapter.can_handle should accept .pdf and .docx."""
        adapter = ResumeAdapter()
        assert adapter.can_handle("resume.pdf") is True
        assert adapter.can_handle("resume.docx") is True
        assert adapter.can_handle("resume.csv") is False

    def test_returns_empty_on_missing_file(self):
        """ResumeAdapter.load should return [] for a missing file."""
        assert ResumeAdapter().load("/nonexistent/resume.pdf") == []
