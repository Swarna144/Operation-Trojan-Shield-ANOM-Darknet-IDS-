# Operation-Trojan-Shield-ANOM-Darknet-IDS-
To study how ANOM worked, why the usual defences and the usual assumptions of darknet users failed to expose it, and what defenders can learn from the way it was built.

**Group 14**: Aaradhya, Prachi, Mudita, Swarna. 
Faculty: Dr. Mangal Singh.

This repository holds the code and report for our case study of **Operation Trojan Shield** (the FBI/AFP-run ANOM encrypted-phone platform, 2018-2021). The ANOM operators never broke the encryption. They ran the platform and controlled the key handling, so the trust users placed in the vendor was the weak point.

## What the project asks

Could a standard network intrusion detection system (IDS) have noticed that ANOM copied every message to a hidden recipient? We test this with a small **synthetic** experiment.

| Hypothesis | Setting | Expected result |
|---|---|---|
| H1 | Detector has a clean reference without the hidden recipient | Detectable only with enough overhead **and** enough messages observed |
| H2 | Hidden recipient is already part of "normal" (closed ecosystem from day one) | Chance level (AUC about 0.5) however long we watch |
| H3 | Bolt-on design copying to a separate, never-seen server | Easily detected (new-destination rule) |

## Method

- **Traffic**: log-normal message size (median 700 B, sigma 0.8) and gap between messages (median 20 s, sigma 1.2).
- **Hidden recipient**: 0, 32, 64, 128, 256 or 512 extra bytes added to every message (assumed values).
- **Detector** (unsupervised): for a window of *n* messages, take the mean of (log size, log gap) and compute the squared Mahalanobis distance from the baseline mean, scaled by *n*.
- **Scenarios**: A uses a clean baseline, B uses a baseline that already carries a 128-byte overhead, and C is a bolt-on copy to a new server, detected by an unseen-destination rule.
- **Metrics**: ROC AUC and detection rate at about 1% false alarms. Seed 14, 4,000 windows per class, 50,000 baseline flows.

## Run it

```bash
pip install -r requirements.txt
python src/run_experiment.py     # writes results/*.csv and results/figure5.png
pytest -q tests                  # checks that H1, H2 and H3 hold
```

## Results (this repo's run)

Scenario A, detection AUC with a clean reference (0.5 = chance):

| Overhead (B) | 1 msg | 10 msgs | 100 msgs | Detection rate, 100 msgs, ~1% FA |
|---|---|---|---|---|
| 0 | 0.51 | 0.52 | 0.52 | 1.1% |
| 32 | 0.49 | 0.48 | 0.56 | 1.8% |
| 64 | 0.47 | 0.50 | 0.71 | 7.3% |
| 128 | 0.46 | 0.55 | 0.94 | 42.7% |
| 256 | 0.45 | 0.72 | 1.00 | 99.6% |
| 512 | 0.49 | 0.94 | 1.00 | 100% |

Scenario B stays at chance (AUC about 0.50, detection about 1%). Scenario C detects 100% of bolt-on flows with 0.5% false alarms. The numbers match the report's Table 8 to within a few points. They are not bit-identical because the random-number stream differs.

![Results]<img width="1650" height="600" alt="figure5" src="https://github.com/user-attachments/assets/58b1cecd-7318-4b17-8d68-156e952756ed" />


## Takeaways

1. Network IDS cannot catch a threat that is built into the trusted tool itself.
2. Detection needs a clean reference. In a closed ecosystem like ANOM nobody had one.
3. Auditing the application, meaning the supply chain, is a stronger control than watching the network.

## Limits

The data are synthetic and the overheads are our assumptions. Real ANOM traffic is not public and has many more features. The model treats messages as independent. **The results are not evidence about the real ANOM network.**

## Repository layout

```
src/anom_sim.py        traffic generator, detector, scenarios
src/run_experiment.py  runs everything, writes tables and figure
tests/test_sim.py      checks the three hypotheses
results/               CSV tables and figure
docs/                  the full case study report (.docx)
```

