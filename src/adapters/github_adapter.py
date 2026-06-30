"""Adapter for public GitHub profiles via the REST API."""
from __future__ import annotations

import logging
from typing import Optional
from urllib.parse import urlparse

import requests

from src.adapters.base import BaseAdapter
from src.models.raw_record import RawRecord, RawSkill

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


class GitHubAdapter(BaseAdapter):
    """Fetches candidate data from a public GitHub profile.

    Skills are inferred from the primary language of each public repo.
    """

    SOURCE_NAME = "github"

    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token
        session = requests.Session()
        session.headers["User-Agent"] = "eightfold-candidate-pipeline/1.0"
        if token:
            session.headers["Authorization"] = f"Bearer {token}"
        self._session = session

    def can_handle(self, path: str) -> bool:
        try:
            url = path if "://" in path else f"https://{path}"
            parsed = urlparse(url)
            if "github.com" not in (parsed.netloc or ""):
                return False
            segments = [s for s in parsed.path.strip("/").split("/") if s]
            return len(segments) == 1
        except Exception:
            return False

    def load(self, path: str) -> list[RawRecord]:
        try:
            username = self._extract_username(path)
            user_data = self._fetch_user(username)
            if not user_data:
                return []
            repos_data = self._fetch_repos(username)
            skills = self._extract_languages(repos_data)

            lang_counts: dict[str, int] = {}
            for repo in repos_data:
                lang = repo.get("language")
                if lang:
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1

            blog = user_data.get("blog") or None
            if blog and not blog.startswith("http"):
                blog = f"https://{blog}"

            return [RawRecord(
                source_name=self.SOURCE_NAME,
                source_path=path,
                full_name=user_data.get("name"),
                location_city=user_data.get("location"),
                headline=user_data.get("bio"),
                github_url=user_data.get("html_url"),
                portfolio_url=blog,
                skills=skills,
                extra={
                    "github_repo_count": user_data.get("public_repos", 0),
                    "language_counts": lang_counts,
                },
            )]
        except Exception as exc:
            logger.warning("GitHub adapter error for %s: %s", path, exc)
            return []

    def _extract_username(self, url: str) -> str:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        return parsed.path.strip("/").split("/")[0]

    def _fetch_user(self, username: str) -> dict:
        try:
            resp = self._session.get(f"{GITHUB_API_BASE}/users/{username}", timeout=10)
            if resp.status_code in (404, 403):
                return {}
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.warning("GitHub user fetch failed for %s: %s", username, exc)
            return {}

    def _fetch_repos(self, username: str) -> list[dict]:
        try:
            resp = self._session.get(
                f"{GITHUB_API_BASE}/users/{username}/repos",
                params={"per_page": 100, "sort": "updated"},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.warning("GitHub repos fetch failed for %s: %s", username, exc)
            return []

    def _extract_languages(self, repos: list[dict]) -> list[RawSkill]:
        seen: set[str] = set()
        skills: list[RawSkill] = []
        for repo in repos:
            lang = repo.get("language")
            if lang and lang not in seen:
                seen.add(lang)
                skills.append(RawSkill(name=lang, source_name=self.SOURCE_NAME))
        return skills
