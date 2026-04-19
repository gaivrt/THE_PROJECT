"""Tests for the responsible-disclosure leak scanner.

These tests use only fabricated, syntactically-valid-looking strings -
never real keys.
"""

from __future__ import annotations

from tools.leak_scanner import (
    KEY_RE,
    build_anthropic_email,
    build_issue_body,
    redact,
)

FAKE_KEY = "sk-ant-api03-" + "A" * 95  # 108 chars, matches the public format


class TestKeyRegex:
    def test_matches_fabricated_key(self) -> None:
        assert KEY_RE.search(f"API_KEY={FAKE_KEY}") is not None

    def test_matches_admin_variant(self) -> None:
        admin = "sk-ant-admin01-" + "B" * 90
        assert KEY_RE.search(admin) is not None

    def test_does_not_match_short_string(self) -> None:
        assert KEY_RE.search("sk-ant-api03-tooShort") is None

    def test_does_not_match_unrelated_text(self) -> None:
        assert KEY_RE.search("nothing to see here") is None


class TestRedact:
    def test_never_returns_full_key(self) -> None:
        out = redact(FAKE_KEY)
        assert FAKE_KEY not in out

    def test_includes_length(self) -> None:
        assert "len=108" in redact(FAKE_KEY)

    def test_short_input_safe(self) -> None:
        out = redact("short")
        assert "len=5" in out


class TestEmailDraft:
    def test_does_not_include_full_key(self) -> None:
        findings = [
            {
                "repo_full_name": "alice/example",
                "path": ".env",
                "html_url": "https://github.com/alice/example/blob/abc/.env",
                "key_prefix": FAKE_KEY[:16],
                "key_length": len(FAKE_KEY),
            }
        ]
        text = build_anthropic_email(findings)
        assert FAKE_KEY not in text
        assert "alice/example" in text
        assert "security@anthropic.com" in text


class TestIssueBody:
    def test_no_key_material_in_issue(self) -> None:
        body = build_issue_body(".env")
        assert FAKE_KEY not in body
        assert "console.anthropic.com" in body
        assert ".env" in body
