"""Run scenarios A, B, C; write CSV tables and the figure to results/."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from anom_sim import run, WINDOWS

OUT = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(OUT, exist_ok=True)
res = run()

with open(os.path.join(OUT, "scenario_a.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["overhead_bytes", "auc_1_msg", "auc_10_msg", "auc_100_msg", "detection_rate_100_msg_at_1pct_FA"])
    for r in res["A"]:
        w.writerow([r["overhead"], f'{r["auc_1"]:.2f}', f'{r["auc_10"]:.2f}', f'{r["auc_100"]:.2f}', f'{100*r["det_rate_100"]:.1f}%'])
with open(os.path.join(OUT, "scenarios_b_c.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["scenario", "messages", "auc", "detection_rate"])
    for n, v in res["B"].items():
        w.writerow(["B", n, f'{v["auc"]:.2f}', f'{100*v["det_rate"]:.1f}%'])
    w.writerow(["C", "-", "-", f'{100*res["C"]["det_rate"]:.0f}% (false alarms {100*res["C"]["false_alarm"]:.1f}%)'])

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ov = [r["overhead"] for r in res["A"]]
for n in WINDOWS:
    ax[0].plot(ov, [r[f"auc_{n}"] for r in res["A"]], marker="o", label=f"{n} message(s)")
ax[0].axhline(0.5, color="gray", ls="--", lw=1)
ax[0].set(xlabel="Hidden-recipient overhead (bytes)", ylabel="AUC", title="(a) Scenario A: clean reference")
ax[0].legend()
a128 = next(r for r in res["A"] if r["overhead"] == 128)["det_rate_100"]
vals = [a128, res["B"][100]["det_rate"], res["C"]["det_rate"]]
ax[1].bar(["A (128 B)", "B (baseline\nhas overhead)", "C (bolt-on)"], [100*v for v in vals], color=["#4c72b0", "#8c8c8c", "#55a868"])
ax[1].set(ylabel="Detection rate at ~1% false alarms (%)", title="(b) Scenarios A, B, C")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "figure5.png"), dpi=150)
print(open(os.path.join(OUT, "scenario_a.csv")).read()); print(open(os.path.join(OUT, "scenarios_b_c.csv")).read())
