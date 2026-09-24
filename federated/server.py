"""
server.py - Central Federated Learning Server with FedAvg Aggregation

Maintains the global model parameters, coordinates communication rounds,
and performs Federated Averaging (FedAvg) on client updates received
with Differential Privacy protection.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np


class FederatedServer:
    """
    Central aggregation server implementing Federated Averaging (FedAvg).
    
    Attributes:
        weights (np.ndarray): Current global model parameters.
        round_num (int): Current communication round index.
        history (List[Dict[str, Any]]): Metrics logged per round.
    """

    def __init__(self, feature_dim: int = 6, random_seed: Optional[int] = 42):
        self.feature_dim = feature_dim
        rng = np.random.RandomState(random_seed)
        self.weights = rng.normal(0, 0.5, size=feature_dim)
        self.round_num = 0
        self.history: List[Dict[str, Any]] = []

        # Create validation dataset to measure global convergence
        self.val_X = rng.normal(0, 1.0, size=(200, feature_dim))
        true_w = np.array([1.5, -2.0, 0.8, -1.2, 0.5, -0.3][:feature_dim])
        val_logits = np.dot(self.val_X, true_w)
        self.val_y = 1.0 / (1.0 + np.exp(-val_logits))

    def aggregate_fedavg(self, client_results: List[Dict[str, Any]]) -> np.ndarray:
        """
        Aggregate client updates using weighted FedAvg:
            global_update = sum( (n_k / total_n) * update_k )
            
        Returns:
            np.ndarray: Updated global weights.
        """
        if not client_results:
            return self.weights

        total_samples = sum(c["num_samples"] for c in client_results)
        weighted_update = np.zeros_like(self.weights)

        for client in client_results:
            weight_factor = client["num_samples"] / total_samples
            weighted_update += weight_factor * client["update"]

        # Update global parameters
        self.weights = self.weights + weighted_update
        self.round_num += 1

        # Evaluate performance on validation set
        val_loss, val_acc = self.evaluate(self.weights)

        round_metric = {
            "round": self.round_num,
            "val_loss": float(val_loss),
            "val_accuracy": float(val_acc),
            "update_norm": float(np.linalg.norm(weighted_update)),
            "participating_clients": len(client_results),
            "total_samples": total_samples,
        }
        self.history.append(round_metric)

        return self.weights

    def evaluate(self, weights: Optional[np.ndarray] = None) -> Tuple[float, float]:
        """
        Evaluate model parameters on validation set.
        
        Returns:
            (loss, binary_classification_accuracy)
        """
        w = self.weights if weights is None else weights
        preds = 1.0 / (1.0 + np.exp(-np.dot(self.val_X, w)))

        # Binary cross entropy loss with numerical clipping
        eps = 1e-7
        clipped_preds = np.clip(preds, eps, 1.0 - eps)
        loss = -np.mean(self.val_y * np.log(clipped_preds) + (1.0 - self.val_y) * np.log(1.0 - clipped_preds))

        # Binary accuracy (threshold at 0.5)
        binary_pred = (preds >= 0.5).astype(int)
        binary_true = (self.val_y >= 0.5).astype(int)
        accuracy = float(np.mean(binary_pred == binary_true))

        return float(loss), accuracy
