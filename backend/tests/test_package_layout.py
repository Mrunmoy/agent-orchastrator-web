"""Tests that the backend package layout is importable and correctly structured."""

import importlib


def test_root_package_imports():
    mod = importlib.import_module("agent_orchestrator")
    assert mod is not None


def test_orchestrator_subpackage_imports():
    mod = importlib.import_module("agent_orchestrator.orchestrator")
    assert mod is not None


def test_adapters_subpackage_imports():
    mod = importlib.import_module("agent_orchestrator.adapters")
    assert mod is not None


def test_api_subpackage_imports():
    mod = importlib.import_module("agent_orchestrator.api")
    assert mod is not None


def test_api_routes_subpackage_imports():
    mod = importlib.import_module("agent_orchestrator.api.routes")
    assert mod is not None


def test_storage_subpackage_imports():
    mod = importlib.import_module("agent_orchestrator.storage")
    assert mod is not None


def test_runtime_subpackage_imports():
    mod = importlib.import_module("agent_orchestrator.runtime")
    assert mod is not None
