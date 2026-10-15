import json
from pathlib import Path

import pandas as pd
import pytest

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(scope="session")
def accounts():
    return pd.read_csv(DATA / "accounts.csv", parse_dates=["created_at"])


@pytest.fixture(scope="session")
def devices():
    return pd.read_csv(DATA / "devices.csv")


@pytest.fixture(scope="session")
def txns():
    return pd.read_csv(DATA / "transactions.csv", parse_dates=["timestamp"])


@pytest.fixture(scope="session")
def expected():
    with open(DATA / "expected_results.json") as f:
        return json.load(f)