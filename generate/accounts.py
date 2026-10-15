import numpy as np
import pandas as pd

SEED = 42
REFERENCE_DATE = pd.Timestamp("2026-10-01")
N_ACCOUNTS = 200

rng = np.random.default_rng(SEED)

FIRST_NAMES = ["Aarav", "Riya", "Kabir", "Meera", "Rohan", "Ananya", "Vikram", "Isha"]
LAST_NAMES = ["Sharma", "Verma", "Nair", "Reddy", "Singh", "Iyer", "Gupta", "Das"]
BANK_HANDLES = {"SBI": "synsbi", "HDFC": "synhdfc", "ICICI": "synicici", "AXIS": "synaxis"}


def make_accounts(n=N_ACCOUNTS):
    ids = [f"ACC{i:04d}" for i in range(1, n + 1)]
    first = rng.choice(FIRST_NAMES, n)
    last = rng.choice(LAST_NAMES, n)
    bank = rng.choice(list(BANK_HANDLES), n)

    vpa = [
        f"{f.lower()}.{l.lower()}{i}@{BANK_HANDLES[b]}"
        for i, (f, l, b) in enumerate(zip(first, last, bank), start=1)
    ]
    days_ago = rng.integers(30, 1500, n)
    created = REFERENCE_DATE - pd.to_timedelta(days_ago, unit="D")

    return pd.DataFrame({
        "account_id": ids,
        "holder_name": [f"{f} {l}" for f, l in zip(first, last)],
        "vpa": vpa,
        "bank": bank,
        "created_at": created,
    })


if __name__ == "__main__":
    df = make_accounts()
    df.to_csv("data/accounts.csv", index=False)
    print(df.head())
    print("Rows:", len(df))
    print("VPAs unique:", df["vpa"].is_unique)