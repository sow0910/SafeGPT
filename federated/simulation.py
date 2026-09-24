"""
simulation.py - Federated Learning & Differential Privacy Multi-Round Simulation

Coordinates simulated edge organizations (Hospital A, Hospital B, Hospital C)
collaborating through the FederatedServer. Demonstrates how FedAvg converges
and compares the privacy-utility tradeoff across different DP epsilon values.
"""

from typing import Dict, Any, List, Optional
import numpy as np

from .client import FederatedClient
from .server import FederatedServer


def setup_clients(feature_dim: int = 6) -> List[FederatedClient]:
    """Create 3 representative simulated enterprise/healthcare clients."""
    clients = [
        FederatedClient(client_id="Hospital_A", num_samples=300, feature_dim=feature_dim, random_seed=101),
        FederatedClient(client_id="Hospital_B", num_samples=200, feature_dim=feature_dim, random_seed=202),
        FederatedClient(client_id="Hospital_C", num_samples=150, feature_dim=feature_dim, random_seed=303),
    ]
    return clients


def run_federated_simulation(
    rounds: int = 5,
    use_dp: bool = True,
    epsilon: float = 1.0,
    delta: float = 1e-5,
    max_norm: float = 1.0,
    local_epochs: int = 3,
    lr: float = 0.05,
    clients: Optional[List[FederatedClient]] = None,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """
    Execute a multi-round Federated Learning simulation with optional Differential Privacy.

    Returns:
        Dict containing round history, initial vs final metrics, and client audit logs.
    """
    feature_dim = 6
    if clients is None:
        clients = setup_clients(feature_dim=feature_dim)

    server = FederatedServer(feature_dim=feature_dim, random_seed=random_seed)

    initial_loss, initial_acc = server.evaluate()
    client_audit_history = []

    for r in range(1, rounds + 1):
        round_client_updates = []

        # Each client computes local update on private data
        for client in clients:
            client_result = client.get_protected_update(
                global_weights=server.weights,
                use_dp=use_dp,
                max_norm=max_norm,
                epsilon=epsilon,
                delta=delta,
                epochs=local_epochs,
                lr=lr,
            )
            round_client_updates.append(client_result)

        client_audit_history.append({
            "round": r,
            "client_summaries": [
                {
                    "client_id": c["client_id"],
                    "raw_norm": c["raw_norm"],
                    "clipped_norm": c["clipped_norm"],
                    "noise_added": c["use_dp"],
                }
                for c in round_client_updates
            ]
        })

        # Server aggregates via FedAvg without seeing raw client data
        server.aggregate_fedavg(round_client_updates)

    final_loss, final_acc = server.evaluate()

    return {
        "use_dp": use_dp,
        "epsilon": epsilon if use_dp else None,
        "delta": delta if use_dp else None,
        "max_norm": max_norm,
        "rounds": rounds,
        "initial_loss": initial_loss,
        "initial_acc": initial_acc,
        "final_loss": final_loss,
        "final_acc": final_acc,
        "round_history": server.history,
        "client_audit_history": client_audit_history,
        "final_weights": server.weights.tolist(),
    }


def compare_dp_tradeoffs(rounds: int = 5) -> List[Dict[str, Any]]:
    """
    Runs comparison across privacy regimes:
    Experiment A: FL without DP
    Experiment B: FL with DP at ε ∈ {0.5, 1.0, 2.0, 5.0}
    """
    scenarios = [
        {"name": "FL without DP (Baseline)", "use_dp": False, "epsilon": 0.0, "privacy": "None (ε → ∞)"},
        {"name": "FL with DP (ε = 0.5, Stronger)", "use_dp": True, "epsilon": 0.5, "privacy": "Stronger"},
        {"name": "FL with DP (ε = 1.0, Strong)", "use_dp": True, "epsilon": 1.0, "privacy": "Strong"},
        {"name": "FL with DP (ε = 2.0, Moderate)", "use_dp": True, "epsilon": 2.0, "privacy": "Moderate"},
        {"name": "FL with DP (ε = 5.0, Weaker)", "use_dp": True, "epsilon": 5.0, "privacy": "Weaker"},
    ]

    results = []
    for sc in scenarios:
        res = run_federated_simulation(
            rounds=rounds,
            use_dp=sc["use_dp"],
            epsilon=sc["epsilon"],
            random_seed=42,
        )
        round_accs = [h["val_accuracy"] for h in res["round_history"]]
        results.append({
            "scenario": sc["name"],
            "use_dp": sc["use_dp"],
            "epsilon": None if not sc["use_dp"] else sc["epsilon"],
            "privacy": sc["privacy"],
            "rounds": rounds,
            "initial_accuracy": res["initial_acc"],
            "initial_loss": res["initial_loss"],
            "final_accuracy": res["final_acc"],
            "final_loss": res["final_loss"],
            "round_accuracies": round_accs,
            "history": res["round_history"],
        })

    return results


if __name__ == "__main__":
    print("=== Running SafeGPT Federated Learning Simulation ===")
    sim = run_federated_simulation(rounds=5, use_dp=True, epsilon=1.0)
    print(f"Rounds: {sim['rounds']}")
    print(f"Initial Acc: {sim['initial_acc']:.4f} | Initial Loss: {sim['initial_loss']:.4f}")
    print(f"Final Acc  : {sim['final_acc']:.4f} | Final Loss: {sim['final_loss']:.4f}")
    for rh in sim["round_history"]:
        print(f" Round {rh['round']}: Loss={rh['val_loss']:.4f}, Acc={rh['val_accuracy']:.4f}")
