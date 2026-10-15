"""Synthetic experiment for the case study
"Operation Trojan Shield (ANOM): Darknet Trust, Encrypted Communication and
the Limits of Intrusion Detection" (Group 14).

All traffic is synthetic; the parameters are assumptions (see README, Table 5).
The real ANOM traffic is not public, so results say how detectability depends on
design, not how detectable the real ANOM network was.
"""
import numpy as np

SEED = 14
SIZE_MEDIAN, SIZE_SIGMA = 700.0, 0.8      # bytes, log-normal
GAP_MEDIAN, GAP_SIGMA = 20.0, 1.2         # seconds, log-normal
OVERHEADS = [0, 32, 64, 128, 256, 512]    # hidden-recipient bytes per message
WINDOWS = [1, 10, 100]                    # messages observed before a decision
N_WINDOWS = 4000                          # windows per class
N_BASELINE = 50000                        # baseline flows
NEW_DEST_RATE = 0.005                     # normal-traffic new-destination rate
FALSE_ALARM = 0.01                        # target false-alarm rate


def messages(rng, shape, overhead=0):
    """Log-size and log-gap features for synthetic messages."""
    size = rng.lognormal(np.log(SIZE_MEDIAN), SIZE_SIGMA, shape) + overhead
    gap = rng.lognormal(np.log(GAP_MEDIAN), GAP_SIGMA, shape)
    return np.stack([np.log(size), np.log(gap)], axis=-1)


class Detector:
    """Unsupervised anomaly detector: n * squared Mahalanobis distance of the
    window mean from the baseline mean."""

    def __init__(self, baseline):
        flat = baseline.reshape(-1, 2)
        self.mu = flat.mean(axis=0)
        self.inv = np.linalg.inv(np.cov(flat, rowvar=False))

    def score(self, windows):
        n = windows.shape[1]
        d = windows.mean(axis=1) - self.mu
        return n * np.einsum("ij,jk,ik->i", d, self.inv, d)


def auc(neg, pos):
    """Area under the ROC curve via the rank-sum (Mann-Whitney) statistic."""
    allv = np.concatenate([neg, pos])
    ranks = allv.argsort().argsort() + 1.0
    return (ranks[len(neg):].sum() - len(pos) * (len(pos) + 1) / 2) / (len(neg) * len(pos))


def detection_rate(neg, pos, fa=FALSE_ALARM):
    thr = np.quantile(neg, 1 - fa)
    return float((pos > thr).mean())


def scenario_a(rng):
    """Clean reference; test traffic carries the overhead."""
    rows = []
    baseline = messages(rng, (N_BASELINE, 1))
    det = Detector(baseline)
    for oh in OVERHEADS:
        row = {"overhead": oh}
        for n in WINDOWS:
            neg = det.score(messages(rng, (N_WINDOWS, n)))
            pos = det.score(messages(rng, (N_WINDOWS, n), oh))
            row[f"auc_{n}"] = auc(neg, pos)
            if n == 100:
                row["det_rate_100"] = detection_rate(neg, pos)
        rows.append(row)
    return rows


def scenario_b(rng, overhead=128):
    """Baseline already carries the overhead (closed ecosystem from day one)."""
    det = Detector(messages(rng, (N_BASELINE, 1), overhead))
    out = {}
    for n in WINDOWS:
        neg = det.score(messages(rng, (N_WINDOWS, n), overhead))
        pos = det.score(messages(rng, (N_WINDOWS, n), overhead))
        out[n] = {"auc": auc(neg, pos), "det_rate": detection_rate(neg, pos)}
    return out


def scenario_c(rng):
    """Bolt-on copy to a never-seen server; rule: alert on unseen destination."""
    normal_alerts = rng.random(N_WINDOWS * 10) < NEW_DEST_RATE
    bolt_on_alerts = np.ones(N_WINDOWS * 10, dtype=bool)
    return {"det_rate": float(bolt_on_alerts.mean()),
            "false_alarm": float(normal_alerts.mean())}


def run(seed=SEED):
    rng = np.random.default_rng(seed)
    return {"A": scenario_a(rng), "B": scenario_b(rng), "C": scenario_c(rng)}
