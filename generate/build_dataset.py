import json

import numpy as np
import pandas as pd
import networkx as nx
from transactions import make_background_txns

SEED = 45
rng = np.random.default_rng(SEED)

CHAIN = ["ACC0011", "ACC0012", "ACC0013", "ACC0014"]
SHOP = "ACC0020"
CUSTOMERS = ["ACC0021", "ACC0022", "ACC0023", "ACC0024", "ACC0025", "ACC0026"]
SUPPLIER = "ACC0027"
HUB = "ACC0030"
FEEDERS = [f"ACC{i:04d}" for i in range(31, 61)]
ORGANIZER = "ACC0070"
DONORS = [f"ACC{i:04d}" for i in range(71, 101)]
CYCLE = ["ACC0101", "ACC0102", "ACC0103"]
ROOMMATES = ["ACC0111", "ACC0112", "ACC0113"]


VICTIMS_A = [f"ACC{i:04d}" for i in range(121, 126)]
MULES = [f"ACC{i:04d}" for i in range(131, 136)]
COLLECTOR = "ACC0140"
VICTIMS_B = [f"ACC{i:04d}" for i in range(151, 156)]
RECIPIENTS = [f"ACC{i:04d}" for i in range(161, 166)]

FAN_SOURCE = "ACC0142"
SPLITTER = "ACC0141"
FAN_TARGETS = [f"ACC{i:04d}" for i in range(143, 151)]

EMPLOYER = "ACC0061"
EMPLOYEES = [f"ACC{i:04d}" for i in range(62, 70)]

COMPLAINT_SCENARIOS = {
    "S07_CONVERGENCE": VICTIMS_A,
    "S08_UNRELATED_COMPLAINTS": VICTIMS_B,
}
SINK = "ACC0170"
SHARED_A = [f"ACC{i:04d}" for i in range(171, 179)]
DEVICE_A = "DEV9001"

FAMILY = [f"ACC{i:04d}" for i in range(181, 186)]
DEVICE_B = "DEV9002"
SHOPS = [f"ACC{i:04d}" for i in range(191, 201)]

PLANTED_LINKS = pd.DataFrame(
    [{"device_id": DEVICE_A, "account_id": a} for a in SHARED_A]
    + [{"device_id": DEVICE_B, "account_id": a} for a in FAMILY]
)
def scenario_shared_device(acc_to_vpa, acc_to_dev):
    dev = {**acc_to_dev, **{a: DEVICE_A for a in SHARED_A}}
    start = pd.Timestamp("2026-09-29 02:00:00")
    rows = []
    for sender in SHARED_A:
        ts = start + pd.Timedelta(minutes=int(rng.integers(0, 45)),
                                  seconds=int(rng.integers(0, 60)))
        amt = float(np.round(rng.uniform(4000, 4500), 2))
        rows.append(make_txn(ts, sender, SINK, amt, "S09_SHARED_DEVICE_COORDINATED",
                             acc_to_vpa, dev))
    return rows
def scenario_family_phone(acc_to_vpa, acc_to_dev):
    dev = {**acc_to_dev, **{a: DEVICE_B for a in FAMILY}}
    start = pd.Timestamp("2026-09-08")
    rows = []
    for member in FAMILY:
        for _ in range(6):
            ts = start + pd.Timedelta(days=int(rng.integers(0, 21)),
                                      hours=int(rng.integers(8, 22)),
                                      minutes=int(rng.integers(0, 60)))
            shop = SHOPS[int(rng.integers(0, len(SHOPS)))]
            amt = float(np.clip(np.round(rng.lognormal(6.0, 0.8), 2), 50, 5000))
            rows.append(make_txn(ts, member, shop, amt, "S10_FAMILY_PHONE",
                                 acc_to_vpa, dev))
    return rows
def build_lookups(accounts, devices):
    acc_to_vpa = dict(zip(accounts["account_id"], accounts["vpa"]))
    acc_to_dev = devices.groupby("account_id")["device_id"].first().to_dict()
    return acc_to_vpa, acc_to_dev
def make_txn(ts, sender_acc, receiver_acc, amount, scenario_id, acc_to_vpa, acc_to_dev):
    return {
        "timestamp": ts,
        "sender_vpa": acc_to_vpa[sender_acc],
        "receiver_vpa": acc_to_vpa[receiver_acc],
        "amount": amount,
        "txn_type": "PAY",
        "status": "SUCCESS",
        "device_id": acc_to_dev[sender_acc],
        "scenario_id": scenario_id,
    }
def scenario_rapid_chain(acc_to_vpa, acc_to_dev):
    t = pd.Timestamp("2026-09-20 22:40:00")
    amount = 48000.00
    rows = []
    for sender, receiver in zip(CHAIN[:-1], CHAIN[1:]):
        rows.append(make_txn(t, sender, receiver, amount, "S01_RAPID_CHAIN",
                             acc_to_vpa, acc_to_dev))
        gap = pd.Timedelta(minutes=int(rng.integers(2, 9)),
                           seconds=int(rng.integers(0, 60)))
        t = t + gap
        amount = round(amount * 0.95, 2)
    return rows
def scenario_shop_supplier(acc_to_vpa, acc_to_dev):
    day = pd.Timestamp("2026-09-22")
    rows = []
    total = 0.0
    for customer in CUSTOMERS:
        ts = day + pd.Timedelta(hours=int(rng.integers(10, 18)),
                                minutes=int(rng.integers(0, 60)))
        amt = float(np.round(rng.uniform(300, 2000), 2))
        total += amt
        rows.append(make_txn(ts, customer, SHOP, amt, "S02_SHOP_SUPPLIER",
                             acc_to_vpa, acc_to_dev))
    pay_ts = day + pd.Timedelta(hours=19, minutes=30)
    rows.append(make_txn(pay_ts, SHOP, SUPPLIER, round(total * 0.7, 2),
                         "S02_SHOP_SUPPLIER", acc_to_vpa, acc_to_dev))
    return rows    
def scenario_many_sources(acc_to_vpa, acc_to_dev):
    start = pd.Timestamp("2026-09-25 14:00:00")
    rows = []
    for sender in FEEDERS:
        ts = start + pd.Timedelta(minutes=int(rng.integers(0, 180)),
                                  seconds=int(rng.integers(0, 60)))
        amt = float(np.round(rng.uniform(1900, 2100), 2))
        rows.append(make_txn(ts, sender, HUB, amt, "S03_MANY_SOURCES",
                             acc_to_vpa, acc_to_dev))
    return rows
def scenario_charity(acc_to_vpa, acc_to_dev):
    start = pd.Timestamp("2026-09-23")
    rows = []
    for donor in DONORS:
        ts = start + pd.Timedelta(days=int(rng.integers(0, 5)),
                                  hours=int(rng.integers(8, 22)),
                                  minutes=int(rng.integers(0, 60)))
        amt = float(np.clip(np.round(rng.lognormal(6.0, 0.8), 2), 100, 5000))
        rows.append(make_txn(ts, donor, ORGANIZER, amt, "S04_CHARITY_COLLECTION",
                             acc_to_vpa, acc_to_dev))
    return rows  
def scenario_cycle(acc_to_vpa, acc_to_dev):
    t = pd.Timestamp("2026-09-27 11:15:00")
    amount = 25000.00
    rows = []
    for i in range(len(CYCLE)):
        sender = CYCLE[i]
        receiver = CYCLE[(i + 1) % len(CYCLE)]
        rows.append(make_txn(t, sender, receiver, amount, "S05_CYCLE",
                             acc_to_vpa, acc_to_dev))
        t = t + pd.Timedelta(minutes=int(rng.integers(10, 41)))
        amount = round(amount * 0.99, 2)
    return rows


def scenario_roommates(acc_to_vpa, acc_to_dev):
    start = pd.Timestamp("2026-09-12 20:00:00")
    plan = [
        (ROOMMATES[0], ROOMMATES[1], 1250.00, 0),
        (ROOMMATES[1], ROOMMATES[2], 640.00, 2),
        (ROOMMATES[2], ROOMMATES[0], 980.00, 4),
    ]
    rows = []
    for sender, receiver, amt, days in plan:
        ts = start + pd.Timedelta(days=days, minutes=int(rng.integers(0, 240)))
        rows.append(make_txn(ts, sender, receiver, amt, "S06_ROOMMATE_SETTLEUP",
                             acc_to_vpa, acc_to_dev))
    return rows
def scenario_convergence(acc_to_vpa, acc_to_dev):
    day = pd.Timestamp("2026-09-28")
    rows = []
    for victim, mule in zip(VICTIMS_A, MULES):
        t = day + pd.Timedelta(hours=int(rng.integers(10, 19)),
                               minutes=int(rng.integers(0, 60)))
        amt = float(np.round(rng.uniform(8000, 15000), 2))
        rows.append(make_txn(t, victim, mule, amt, "S07_CONVERGENCE",
                             acc_to_vpa, acc_to_dev))
        t2 = t + pd.Timedelta(minutes=int(rng.integers(5, 21)))
        rows.append(make_txn(t2, mule, COLLECTOR, round(amt * 0.94, 2),
                             "S07_CONVERGENCE", acc_to_vpa, acc_to_dev))
    return rows


def scenario_unrelated(acc_to_vpa, acc_to_dev):
    start = pd.Timestamp("2026-09-24")
    rows = []
    for victim, recipient in zip(VICTIMS_B, RECIPIENTS):
        t = start + pd.Timedelta(days=int(rng.integers(0, 5)),
                                 hours=int(rng.integers(9, 22)),
                                 minutes=int(rng.integers(0, 60)))
        amt = float(np.clip(np.round(rng.lognormal(7.0, 0.8), 2), 200, 20000))
        rows.append(make_txn(t, victim, recipient, amt, "S08_UNRELATED_COMPLAINTS",
                             acc_to_vpa, acc_to_dev))
    return rows


def build_complaints(all_txns, acc_to_vpa):
    rows = []
    for sid, victims in COMPLAINT_SCENARIOS.items():
        victim_vpas = {acc_to_vpa[a] for a in victims}
        disputed = all_txns[(all_txns["scenario_id"] == sid)
                            & (all_txns["sender_vpa"].isin(victim_vpas))]
        for _, t in disputed.iterrows():
            filed = t["timestamp"] + pd.Timedelta(days=int(rng.integers(1, 4)))
            rows.append({
                "victim_vpa": t["sender_vpa"],
                "txn_id": t["txn_id"],
                "complaint_date": filed.date(),
            })
    df = (pd.DataFrame(rows)
          .sort_values("complaint_date", kind="stable")
          .reset_index(drop=True))
    df.insert(0, "complaint_id", [f"CMP{i:04d}" for i in range(1, len(df) + 1)])
    return df     
def scenario_fan_out(acc_to_vpa, acc_to_dev):
    t = pd.Timestamp("2026-09-30 15:00:00")
    total = 60000.00
    rows = [make_txn(t, FAN_SOURCE, SPLITTER, total, "S11_FAN_OUT",
                     acc_to_vpa, acc_to_dev)]
    share = round(total * 0.95 / len(FAN_TARGETS), 2)
    for target in FAN_TARGETS:
        ts = t + pd.Timedelta(minutes=int(rng.integers(2, 31)),
                              seconds=int(rng.integers(0, 60)))
        amt = round(share * float(rng.uniform(0.95, 1.05)), 2)
        rows.append(make_txn(ts, SPLITTER, target, amt, "S11_FAN_OUT",
                             acc_to_vpa, acc_to_dev))
    return rows


def scenario_payroll(acc_to_vpa, acc_to_dev):
    pay_day = pd.Timestamp("2026-09-05 10:00:00")
    rows = []
    for employee in EMPLOYEES:
        ts = pay_day + pd.Timedelta(minutes=int(rng.integers(0, 20)))
        amt = float(np.round(rng.uniform(18000, 45000), 2))
        rows.append(make_txn(ts, EMPLOYER, employee, amt, "S12_PAYROLL",
                             acc_to_vpa, acc_to_dev))
    return rows                                    
SCENARIOS = {
    "S01_RAPID_CHAIN": {
        "description": "Funds hop through three accounts within minutes, each passing on 95% of what it received.",
        "should_alert": True,
        "expected_rules": ["rapid_onward_transfer"],
        "accounts": CHAIN,
    },
    "S02_SHOP_SUPPLIER": {
        "description": "Shop receives six customer payments through the day and pays its supplier 70% of the total hours later.",
        "should_alert": False,
        "expected_rules": [],
        "accounts": [SHOP] + CUSTOMERS + [SUPPLIER],
    },
        "S03_MANY_SOURCES": {
        "description": "Thirty unrelated accounts each send about Rs 2,000 to one account within three hours.",
        "should_alert": True,
        "expected_rules": ["multiple_incoming_sources"],
        "accounts": [HUB] + FEEDERS,
    },
    "S04_CHARITY_COLLECTION": {
        "description": "Thirty donors send varied amounts to a fundraiser's account spread over five days.",
        "should_alert": False,
        "expected_rules": [],
        "accounts": [ORGANIZER] + DONORS,
    },
        "S05_CYCLE": {
        "description": "Three accounts pass about Rs 25,000 around a loop within an hour, each hop 1% smaller.",
        "should_alert": True,
        "expected_rules": ["transaction_cycle"],
        "accounts": CYCLE,
    },
    "S06_ROOMMATE_SETTLEUP": {
        "description": "Three roommates settle shared costs in a loop over four days with different amounts.",
        "should_alert": False,
        "expected_rules": [],
        "accounts": ROOMMATES,
    },
        "S07_CONVERGENCE": {
        "description": "Five victims pay five different accounts, which each forward about 94% to one collector within minutes. All five complain.",
        "should_alert": True,
        "expected_rules": ["complaint_convergence"],
        "accounts": VICTIMS_A + MULES + [COLLECTOR],
    },
    "S08_UNRELATED_COMPLAINTS": {
        "description": "Five unrelated victims complain about payments to five different recipients over five days, with no shared destination.",
        "should_alert": False,
        "expected_rules": [],
        "accounts": VICTIMS_B + RECIPIENTS,
    },
        "S09_SHARED_DEVICE_COORDINATED": {
        "description": "Eight accounts on one device each pay the same account about Rs 4,000 to 4,500 within 45 minutes at night.",
        "should_alert": True,
        "expected_rules": ["shared_device"],
        "accounts": SHARED_A + [SINK],
        "devices": [DEVICE_A],
        "note": "Shared device plus coordinated timing and one common receiver.",
    },
    "S10_FAMILY_PHONE": {
        "description": "Five household accounts share one phone and pay various shops over three weeks.",
        "should_alert": False,
        "expected_rules": [],
        "accounts": FAMILY + SHOPS,
        "devices": [DEVICE_B],
        "note": "The device link may be shown as context, but must not raise an alert.",
    },
        "S11_FAN_OUT": {
        "description": "Rs 60,000 arrives and about 95% is split across eight accounts within 30 minutes.",
        "should_alert": True,
        "expected_rules": ["FAN_OUT_SPLITTING"],
        "accounts": [FAN_SOURCE, SPLITTER] + FAN_TARGETS,
    },
    "S12_PAYROLL": {
        "description": "An employer pays eight employees different salaries on payday, with no recent inbound payment.",
        "should_alert": False,
        "expected_rules": [],
        "accounts": [EMPLOYER] + EMPLOYEES,
    },
    
}
if __name__ == "__main__":
    accounts = pd.read_csv("data/accounts.csv", parse_dates=["created_at"])
    devices = pd.read_csv("data/devices.csv")

# Remove old versions of planted device links
    devices = devices[
      ~devices["device_id"].isin(PLANTED_LINKS["device_id"])
]

# Include the new planted links before building lookups
    devices = pd.concat(
        [devices, PLANTED_LINKS],

        ignore_index=True
)

    acc_to_vpa, acc_to_dev = build_lookups(accounts, devices)
    background = make_background_txns(accounts, devices).drop(columns="txn_id")
    background["scenario_id"] = ""

    planted = pd.DataFrame(
        scenario_rapid_chain(acc_to_vpa, acc_to_dev)
        + scenario_shop_supplier(acc_to_vpa, acc_to_dev)
        + scenario_many_sources(acc_to_vpa, acc_to_dev)
        + scenario_charity(acc_to_vpa, acc_to_dev)
        + scenario_cycle(acc_to_vpa, acc_to_dev)
        + scenario_roommates(acc_to_vpa, acc_to_dev)
        + scenario_convergence(acc_to_vpa, acc_to_dev)
        + scenario_unrelated(acc_to_vpa, acc_to_dev)
        + scenario_shared_device(acc_to_vpa, acc_to_dev)
        + scenario_family_phone(acc_to_vpa, acc_to_dev)
        + scenario_fan_out(acc_to_vpa, acc_to_dev)
        + scenario_payroll(acc_to_vpa, acc_to_dev)

    )

    all_txns = pd.concat([background, planted], ignore_index=True)
    all_txns = all_txns.sort_values("timestamp", kind="stable").reset_index(drop=True)
    all_txns.insert(0, "txn_id", [f"TXN{i:06d}" for i in range(1, len(all_txns) + 1)])
    expected = []
    complaints = build_complaints(all_txns, acc_to_vpa)
    complaints.to_csv("data/complaints.csv", index=False)

    expected = []
    for sid, info in SCENARIOS.items():
        ids = all_txns.loc[all_txns["scenario_id"] == sid, "txn_id"].tolist()
        entry = {"scenario_id": sid, **info, "txn_ids": ids}
        if sid in COMPLAINT_SCENARIOS:
            entry["complaint_ids"] = complaints.loc[
                complaints["txn_id"].isin(ids), "complaint_id"
            ].tolist()
        expected.append(entry)

    with open("data/expected_results.json", "w") as f:
        json.dump(expected, f, indent=2)

    all_txns.drop(columns="scenario_id").to_csv("data/transactions.csv", index=False)
    devices.to_csv("data/devices.csv", index=False)
    for sid, victims in COMPLAINT_SCENARIOS.items():
        sub = all_txns[all_txns["scenario_id"] == sid]
        g = nx.DiGraph()
        g.add_edges_from(zip(sub["sender_vpa"], sub["receiver_vpa"]))
        ends = []
        for v in victims:
            reach = nx.descendants(g, acc_to_vpa[v])
            ends.append({n for n in reach if g.out_degree(n) == 0})
        print(sid, "endpoints shared by all victims:", set.intersection(*ends))
        links = pd.read_csv("data/devices.csv")
    per_dev = links.groupby("device_id")["account_id"].nunique()
    print(DEVICE_A, "accounts:", per_dev[DEVICE_A], "|", DEVICE_B, "accounts:", per_dev[DEVICE_B])
    for sid in ["S09_SHARED_DEVICE_COORDINATED", "S10_FAMILY_PHONE"]:
        sub = all_txns[all_txns["scenario_id"] == sid]
        print(sid, "rows:", len(sub), "| devices used:", sub["device_id"].nunique(),
              "| span:", sub["timestamp"].max() - sub["timestamp"].min())    
              