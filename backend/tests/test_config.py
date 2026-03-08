"""Tests for configuration management (T-113)."""

from __future__ import annotations

import os
from unittest.mock import patch

from agent_orchestrator.config import AppConfig, get_config


class TestDefaultConfigValues:
    """TT-113-01: Default config values are used when no env vars are set."""

    def test_default_db_path(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.db_path.endswith(".agent-orchestrator/orchestrator.db")

    def test_default_host(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.host == "0.0.0.0"

    def test_default_port(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.port == 8000

    def test_default_dev_mode(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.dev_mode is False

    def test_default_ollama_url(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.ollama_url == "http://localhost:11434"

    def test_default_log_dir(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.log_dir.endswith(".agent-orchestrator/logs")

    def test_default_personalities_path(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.personalities_path == "config/personalities.json"


class TestEnvOverrides:
    """TT-113-02: Environment variables override default config values."""

    def test_override_db_path(self):
        with patch.dict(os.environ, {"DB_PATH": "/tmp/test.db"}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.db_path == "/tmp/test.db"

    def test_override_host(self):
        with patch.dict(os.environ, {"HOST": "127.0.0.1"}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.host == "127.0.0.1"

    def test_override_port(self):
        with patch.dict(os.environ, {"PORT": "9000"}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.port == 9000

    def test_override_ollama_url(self):
        with patch.dict(
            os.environ, {"OLLAMA_URL": "http://gpu-box:11434"}, clear=True
        ):
            cfg = AppConfig.from_env()
        assert cfg.ollama_url == "http://gpu-box:11434"

    def test_override_log_dir(self):
        with patch.dict(os.environ, {"LOG_DIR": "/var/log/orch"}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.log_dir == "/var/log/orch"

    def test_override_personalities_path(self):
        with patch.dict(
            os.environ, {"PERSONALITIES_PATH": "/etc/orch/p.json"}, clear=True
        ):
            cfg = AppConfig.from_env()
        assert cfg.personalities_path == "/etc/orch/p.json"


class TestDevModeParsing:
    """TT-113-03: DEV_MODE=true is parsed correctly from string env var."""

    def test_dev_mode_true_lowercase(self):
        with patch.dict(os.environ, {"DEV_MODE": "true"}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.dev_mode is True

    def test_dev_mode_true_uppercase(self):
        with patch.dict(os.environ, {"DEV_MODE": "TRUE"}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.dev_mode is True

    def test_dev_mode_one(self):
        with patch.dict(os.environ, {"DEV_MODE": "1"}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.dev_mode is True

    def test_dev_mode_yes(self):
        with patch.dict(os.environ, {"DEV_MODE": "yes"}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.dev_mode is True

    def test_dev_mode_false(self):
        with patch.dict(os.environ, {"DEV_MODE": "false"}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.dev_mode is False

    def test_dev_mode_zero(self):
        with patch.dict(os.environ, {"DEV_MODE": "0"}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.dev_mode is False

    def test_dev_mode_empty(self):
        with patch.dict(os.environ, {"DEV_MODE": ""}, clear=True):
            cfg = AppConfig.from_env()
        assert cfg.dev_mode is False


class TestTildeExpansion:
    """TT-113-04: DB_PATH expands ~ to user home directory."""

    def test_db_path_expands_tilde(self):
        with patch.dict(os.environ, {"DB_PATH": "~/my.db"}, clear=True):
            cfg = AppConfig.from_env()
        assert not cfg.db_path.startswith("~")
        assert cfg.db_path.endswith("/my.db")
        assert cfg.db_path == os.path.expanduser("~/my.db")

    def test_log_dir_expands_tilde(self):
        with patch.dict(os.environ, {"LOG_DIR": "~/logs"}, clear=True):
            cfg = AppConfig.from_env()
        assert not cfg.log_dir.startswith("~")
        assert cfg.log_dir.endswith("/logs")

    def test_default_db_path_is_expanded(self):
        """Default DB_PATH contains ~ and should be expanded."""
        with patch.dict(os.environ, {}, clear=True):
            cfg = AppConfig.from_env()
        assert "~" not in cfg.db_path


class TestGetConfigSingleton:
    """get_config() returns a cached singleton."""

    def test_returns_app_config(self):
        cfg = get_config()
        assert isinstance(cfg, AppConfig)

    def test_same_instance_returned(self):
        # Reset singleton for a clean test
        import agent_orchestrator.config as config_mod

        config_mod._config = None
        a = get_config()
        b = get_config()
        assert a is b

    def test_frozen(self):
        """AppConfig should be immutable."""
        cfg = get_config()
        try:
            cfg.host = "changed"  # type: ignore[misc]
            raise AssertionError("Should have raised FrozenInstanceError")
        except AttributeError:
            pass
