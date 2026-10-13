"""
Pytest configuration for zoo-calrissian-runner tests.

This file sets up the test environment, including paths to CWL wrapper assets.
"""

import os
import re
from pathlib import Path

import pytest
from dotenv import load_dotenv

TEST_LOGS_DIR = Path(
    os.environ.get(
        "TEST_LOGS_DIR", Path(__file__).resolve().parent.parent / "test-logs"
    )
).resolve()


@pytest.fixture(autouse=True)
def isolate_test_logs(request, monkeypatch):
    """
    Run each test from its own directory under TEST_LOGS_DIR.

    pycalrissian copies the tool logs, output and usage report into the
    current working directory, so without this every test overwrites the
    files left by the previous one.
    """
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid).strip("_")
    log_dir = TEST_LOGS_DIR / name
    log_dir.mkdir(parents=True, exist_ok=True)
    for stale in log_dir.iterdir():
        if stale.is_file():
            stale.unlink()
    monkeypatch.chdir(log_dir)
    yield log_dir
    monkeypatch.undo()
    if not any(log_dir.iterdir()):
        log_dir.rmdir()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Configure environment variables for tests.

    Sets up paths to CWL wrapper assets (stagein, stageout) that are needed
    for wrapping workflows during test execution.
    """
    # Load .env file from tests directory
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path, override=True)

    # Get the absolute path to the assets directory
    assets_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "assets")
    )

    # Configure CWL wrapper asset paths
    os.environ["WRAPPER_STAGE_IN"] = os.path.join(assets_dir, "stagein.yaml")
    os.environ["WRAPPER_STAGE_IN_FILE"] = os.path.join(assets_dir, "stagein-file.yaml")
    os.environ["WRAPPER_STAGE_OUT"] = os.path.join(assets_dir, "stageout.yaml")

    # Optional: Set CI_TEST_SKIP to skip integration tests by default
    # Uncomment if you want to skip expensive integration tests
    # if "CI_TEST_SKIP" not in os.environ:
    #     os.environ["CI_TEST_SKIP"] = "1"

    yield

    # Cleanup is optional here since environment variables are process-scoped
