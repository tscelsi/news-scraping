import pytest
import os

@pytest.fixture(autouse=True)
def set_test_env():
    os.environ['ENV'] = 'test'
