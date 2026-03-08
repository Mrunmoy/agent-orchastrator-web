"""Tests for personality profiles loader (T-114)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from agent_orchestrator.config_loaders.personalities import (
    PersonalityProfile,
    get_personality,
    load_personalities,
    _clear_cache,
)


class TestLoadPersonalities:
    """TT-114-01: load_personalities parses valid JSON into PersonalityProfile dataclasses."""

    def setup_method(self):
        _clear_cache()

    def test_parses_valid_json(self, tmp_path: Path):
        data = {
            "software_developer": {
                "label": "Software Developer",
                "traits": ["pragmatic", "test-driven"],
                "instruction": "Act like a senior software engineer.",
            },
            "code_reviewer": {
                "label": "Code Reviewer",
                "traits": ["risk-focused"],
                "instruction": "Prioritize bug risks.",
                "temperature": 0.3,
            },
        }
        p = tmp_path / "personalities.json"
        p.write_text(json.dumps(data))

        result = load_personalities(str(p))

        assert len(result) == 2
        assert "software_developer" in result
        assert "code_reviewer" in result

        dev = result["software_developer"]
        assert isinstance(dev, PersonalityProfile)
        assert dev.key == "software_developer"
        assert dev.display_name == "Software Developer"
        assert dev.system_prompt_fragments == ["Act like a senior software engineer."]
        assert dev.behavioral_constraints == ["pragmatic", "test-driven"]
        assert dev.temperature == 0.7  # default

        reviewer = result["code_reviewer"]
        assert reviewer.temperature == 0.3
        assert reviewer.behavioral_constraints == ["risk-focused"]

    def test_returns_dict_of_profiles(self, tmp_path: Path):
        data = {
            "brainstormer": {
                "label": "Brainstormer",
                "traits": [],
                "instruction": "Be creative.",
            }
        }
        p = tmp_path / "personalities.json"
        p.write_text(json.dumps(data))

        result = load_personalities(str(p))
        assert isinstance(result, dict)
        for key, profile in result.items():
            assert isinstance(key, str)
            assert isinstance(profile, PersonalityProfile)

    def test_multiple_instructions_as_list(self, tmp_path: Path):
        """When instruction is a list, all fragments are preserved."""
        data = {
            "multi": {
                "label": "Multi",
                "traits": [],
                "instruction": ["First instruction.", "Second instruction."],
            }
        }
        p = tmp_path / "personalities.json"
        p.write_text(json.dumps(data))

        result = load_personalities(str(p))
        assert result["multi"].system_prompt_fragments == [
            "First instruction.",
            "Second instruction.",
        ]

    def test_caches_result(self, tmp_path: Path):
        data = {
            "a": {
                "label": "A",
                "traits": [],
                "instruction": "Do A.",
            }
        }
        p = tmp_path / "personalities.json"
        p.write_text(json.dumps(data))

        first = load_personalities(str(p))
        second = load_personalities(str(p))
        assert first is second


class TestLoadPersonalitiesMissingFile:
    """TT-114-02: load_personalities returns empty dict when file doesn't exist."""

    def setup_method(self):
        _clear_cache()

    def test_missing_file_returns_empty_dict(self):
        result = load_personalities("/nonexistent/path/personalities.json")
        assert result == {}
        assert isinstance(result, dict)

    def test_missing_file_does_not_raise(self):
        # Should not raise any exception
        load_personalities("/tmp/surely_does_not_exist_12345.json")


class TestGetPersonality:
    """TT-114-03: get_personality returns None for unknown key."""

    def setup_method(self):
        _clear_cache()

    def test_unknown_key_returns_none(self, tmp_path: Path):
        data = {
            "known": {
                "label": "Known",
                "traits": [],
                "instruction": "Be known.",
            }
        }
        p = tmp_path / "personalities.json"
        p.write_text(json.dumps(data))

        # Load first
        load_personalities(str(p))
        assert get_personality("unknown_key") is None

    def test_known_key_returns_profile(self, tmp_path: Path):
        data = {
            "known": {
                "label": "Known",
                "traits": ["reliable"],
                "instruction": "Be known.",
            }
        }
        p = tmp_path / "personalities.json"
        p.write_text(json.dumps(data))

        load_personalities(str(p))
        result = get_personality("known")
        assert result is not None
        assert isinstance(result, PersonalityProfile)
        assert result.key == "known"
        assert result.display_name == "Known"

    def test_returns_none_when_not_loaded(self):
        """get_personality returns None if load_personalities was never called."""
        assert get_personality("anything") is None
