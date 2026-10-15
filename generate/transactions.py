import numpy as np
import pandas as pd

SEED = 44
REFERENCE_DATE = pd.Timestamp("2026-10-01")
WINDOW_DAYS = 28
N_TXNS = 3000

rng = np.random.default_rng(SEED)
START = REFERENCE_DATE - pd.Timedelta(days=WINDOW_DAYS)

def make_background_txns(accounts, devices, n=N_TXNS):
    vpas = accounts["vpa"].to_numpy()
    n_acc = len(vpas)
    vpa_to_acc = dict(zip(accounts["vpa"], accounts["account_id"]))
    dev_map = devices.groupby("account_id")["device_id"].apply(list).to_dict()
    
    weights = rng.lognormal(mean=0, sigma=1, size=n_acc)
    weights = weights / weights.sum()
    sender_idx = rng.choice(n_acc, size=n, p=weights)

    offset = rng.integers(1, n_acc, size=n)
    receiver_idx = (sender_idx + offset) % n_acc

    sender_vpa = vpas[sender_idx]
    receiver_vpa = vpas[receiver_idx]   

    hour_w = np.array([1, 1, 1, 1, 1, 2, 3, 5, 7, 8, 8, 8,
                       8, 8, 8, 8, 8, 9, 10, 10, 9, 6, 3, 2], dtype=float)
    hour_w = hour_w / hour_w.sum()

    day = rng.integers(0, WINDOW_DAYS, size=n)
    hour = rng.choice(24, size=n, p=hour_w)
    minute = rng.integers(0, 60, size=n)
    second = rng.integers(0, 60, size=n)

    total_sec = day * 86400 + hour * 3600 + minute * 60 + second
    timestamp = START + pd.to_timedelta(total_sec, unit="s")

    amount = np.clip(np.round(rng.lognormal(mean=6.0, sigma=1.0, size=n), 2), 10, 100000)
    txn_type = rng.choice(["PAY", "COLLECT"], size=n, p=[0.85, 0.15])
    status = rng.choice(["SUCCESS", "FAILED"], size=n, p=[0.97, 0.03])

    sender_acc = [vpa_to_acc[v] for v in sender_vpa]
    device_id = [rng.choice(dev_map[a]) for a in sender_acc]     

    df = pd.DataFrame({
        "timestamp": timestamp,
        "sender_vpa": sender_vpa,
        "receiver_vpa": receiver_vpa,
        "amount": amount,
        "txn_type": txn_type,
        "status": status,
        "device_id": device_id,
    })
    df = df.sort_values("timestamp").reset_index(drop=True)
    df.insert(0, "txn_id", [f"TXN{i:06d}" for i in range(1, len(df) + 1)])
    return df   
if __name__ == "__main__":
    accounts = pd.read_csv("data/accounts.csv", parse_dates=["created_at"])
    devices = pd.read_csv("data/devices.csv")
    txns = make_background_txns(accounts, devices)
    txns.to_csv("data/transactions.csv", index=False)

    print(txns.head())
    print("Rows:", len(txns))
    print("Self-transfers:", (txns["sender_vpa"] == txns["receiver_vpa"]).sum())
    print("Amount range:", txns["amount"].min(), "to", txns["amount"].max())
    print("Median amount:", txns["amount"].median())
    print("All txns after accounts opened:",
          txns["timestamp"].min() > accounts["created_at"].max())
    print(txns["txn_type"].value_counts(normalize=True).round(2))

    vpa_to_acc = dict(zip(accounts["vpa"], accounts["account_id"]))
    pairs = set(zip(devices["device_id"], devices["account_id"]))
    bad = [1 for d, v in zip(txns["device_id"], txns["sender_vpa"])
           if (d, vpa_to_acc[v]) not in pairs]
    print("Device not owned by sender:", len(bad))
    all_txns = pd.concat([background, planted], ignore_index=True)
    all_txns = all_txns.sort_values("timestamp", kind="stable").reset_index(drop=True)
    all_txns.insert(0, "txn_id", [f"TXN{i:06d}" for i in range(1, len(all_txns) + 1)])

    complaints = build_complaints(all_txns, acc_to_vpa)
    complaints.to_csv("data/complaints.csv", index=False)

    expected = []
    ...
