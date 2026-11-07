"""Controlled synthetic experiment; never trains on customer conversations."""
import numpy as np


class SecureAggregation:
    """Extension interface. This demo implementation is NOT cryptographically secure."""
    def aggregate(self, updates, sizes):
        return np.average(updates, axis=0, weights=sizes)


def experiment(rounds=8, clip=1.0, noise=0.0, seed=42):
    rng = np.random.default_rng(seed)
    truth = np.array([1.2, -0.7, 0.5, 0.9])
    clients = []
    for node in range(3):
        x = rng.normal(node * .3, 1, (120, 4))
        y = x @ truth + rng.normal(0, .2, 120)
        clients.append((x[:90], y[:90]))
    test_x = rng.normal(0, 1, (200, 4))
    test_y = test_x @ truth
    def train(w, x, y):
        for _ in range(5):
            w = w - .05 * (x.T @ (x @ w - y) / len(y))
        return w
    local = np.zeros(4)
    central = np.zeros(4)
    fed = np.zeros(4)
    all_x = np.concatenate([x for x, _ in clients])
    all_y = np.concatenate([y for _, y in clients])
    history = []
    for r in range(rounds):
        local = train(local, *clients[0])
        central = train(central, all_x, all_y)
        updates = []
        for x, y in clients:
            delta = train(fed.copy(), x, y) - fed
            delta *= min(1, clip / (np.linalg.norm(delta) + 1e-12))
            updates.append(delta + rng.normal(0, noise * clip, 4))
        fed += SecureAggregation().aggregate(updates, [len(y) for _, y in clients])
        history.append(dict(round=r+1, local=float(np.mean((test_x@local-test_y)**2)), centralized=float(np.mean((test_x@central-test_y)**2)), federated=float(np.mean((test_x@fed-test_y)**2))))
    return dict(history=history, clients=3, samples_per_client=90, clip=clip, noise_multiplier=noise, secure_aggregation=False, formal_dp_guarantee=False, dataset='synthetic regression; customer data is never used')
