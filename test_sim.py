import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from anom_sim import run

R = run()

def test_h1_single_message_not_enough():
    for r in R["A"]:
        assert r["auc_1"] < 0.6

def test_h1_100_messages_large_overhead_detectable():
    big = [r for r in R["A"] if r["overhead"] >= 256]
    assert all(r["auc_100"] > 0.98 for r in big)

def test_h2_poisoned_baseline_is_chance():
    for v in R["B"].values():
        assert abs(v["auc"] - 0.5) < 0.03

def test_h3_bolt_on_detected():
    assert R["C"]["det_rate"] == 1.0 and R["C"]["false_alarm"] < 0.01
