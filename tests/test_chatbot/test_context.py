from pathlib import Path

import pytest

from chatbot.context import (
    ProfileSources,
    build_actor_system_prompt,
    build_critic_system_prompt,
    build_critic_user_prompt,
    history_to_text,
    load_profile_sources,
)

_SOURCES = ProfileSources(linkedin="LINKEDIN-TEXT", summary="SUMMARY-TEXT")


def _write_sources(tmp_path: Path) -> tuple[Path, Path]:
    linkedin, summary = tmp_path / "linkedin.txt", tmp_path / "summary.txt"
    linkedin.write_text("  Senior Backend Engineer\n", encoding="utf-8")
    summary.write_text("Lives in Tel Aviv\n", encoding="utf-8")
    return linkedin, summary


def test_load_profile_sources_reads_and_strips_files(tmp_path):
    assert load_profile_sources(*_write_sources(tmp_path)) == ProfileSources("Senior Backend Engineer", "Lives in Tel Aviv")


@pytest.mark.parametrize("text", ["LINKEDIN-TEXT", "SUMMARY-TEXT"])
def test_actor_prompt_includes_sources(text):
    assert text in build_actor_system_prompt(_SOURCES)


def test_actor_prompt_has_no_unfilled_placeholders():
    assert "{" not in build_actor_system_prompt(_SOURCES)


def test_default_profile_files_load():
    assert load_profile_sources().linkedin.startswith("SAMPLE PROFILE")


@pytest.mark.parametrize("text", ["LINKEDIN-TEXT", "SUMMARY-TEXT", "Always answer in Hebrew"])
def test_critic_prompt_includes_sources_and_actor_style(text):
    assert text in build_critic_system_prompt(_SOURCES)


def test_critic_prompt_has_no_unfilled_placeholders():
    assert "{" not in build_critic_system_prompt(_SOURCES)


@pytest.mark.parametrize("history, expected", [
    ([], "(no earlier messages)"),
    ([{"role": "user", "content": "Hi"}], "Visitor: Hi"),
    ([{"role": "assistant", "metadata": None, "content": [{"type": "text", "text": "Hello"}]}], "Chatbot: Hello"),
])
def test_history_to_text(history, expected):
    assert history_to_text(history) == expected


@pytest.mark.parametrize("text", ["Where?", "At Lumenrail", "Visitor: Hi"])
def test_critic_user_prompt_includes_case(text):
    assert text in build_critic_user_prompt("Where?", "At Lumenrail", [{"role": "user", "content": "Hi"}])


def test_critic_prompt_allows_ai_self_disclosure():
    assert "the chatbot is an AI and must say so" in build_critic_system_prompt(_SOURCES)
