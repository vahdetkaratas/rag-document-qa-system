"""
Pytest hooks: keep FastAPI tests fast by not loading sentence-transformers at app startup
(embedding still loads lazily on first embed_texts in slow tests).
"""
import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def _embedding_startup_skip_for_test_session():
    os.environ["EMBEDDING_SKIP_STARTUP_LOAD"] = "1"
    yield
