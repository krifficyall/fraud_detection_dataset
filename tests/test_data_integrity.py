import pandas as pd
def scenario_rows(txns, expected, sid):
    ids = next(s["txn_ids"] for s in expected if s["scenario_id"] == sid)
    return txns[txns["txn_id"].isin(ids)]
def test_s03_many_sources_shape(txns, expected):
    rows = scenario_rows(txns, expected, "S03_MANY_SOURCES")
    assert rows["sender_vpa"].nunique() == 30
    assert rows["receiver_vpa"].nunique() == 1
    span = rows["timestamp"].max() - rows["timestamp"].min()
    assert span <= pd.Timedelta(hours=3)
    assert rows["amount"].max() - rows["amount"].min() <= 200
def test_s04_charity_shape(txns, expected):
    rows = scenario_rows(txns, expected, "S04_CHARITY_COLLECTION")
    assert rows["sender_vpa"].nunique() == 30
    assert rows["receiver_vpa"].nunique() == 1
    span = rows["timestamp"].max() - rows["timestamp"].min()
    assert span >= pd.Timedelta(days=2)        

def test_account_ids_unique(accounts):
    assert accounts["account_id"].is_unique


def test_vpas_unique(accounts):
    assert accounts["vpa"].is_unique


def test_accounts_have_no_missing_values(accounts):
    assert not accounts.isna().any().any()