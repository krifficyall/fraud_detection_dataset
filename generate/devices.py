import numpy as np
import pandas as pd

SEED = 43
rng = np.random.default_rng(SEED)
def make_devices(account_ids):
    shuffled = rng.permutation(account_ids)
    rows = []
    device_no = 1
#giving every account a primary device 
    i = 0
    while i < len(shuffled):
        size = rng.choice([1, 2, 3], p=[0.88, 0.09, 0.03])
        group = shuffled[i:i + size]
        device_id = f"DEV{device_no:04d}"
        for acc in group:
            rows.append({"device_id": device_id, "account_id": acc})
        device_no += 1
        i += size
    n_second = int(len(account_ids) * 0.10)
    second = rng.choice(account_ids, n_second, replace=False)
    for acc in second:
        rows.append({"device_id": f"DEV{device_no:04d}", "account_id": acc})
        device_no += 1
    return pd.DataFrame(rows)
if __name__ == "__main__":
    accounts = pd.read_csv("data/accounts.csv")
    devices = make_devices(accounts["account_id"].to_numpy())
    devices.to_csv("data/devices.csv", index=False)

    print(devices.head())
    print("Links:", len(devices))
    print("Devices:", devices["device_id"].nunique())

    per_device = devices.groupby("device_id")["account_id"].nunique()
    print("Shared devices:", (per_device > 1).sum())

    missing = set(accounts["account_id"]) - set(devices["account_id"])
    print("Accounts with no device:", len(missing))
