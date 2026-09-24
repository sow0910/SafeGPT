"""
client.py - Federated Client with Local Training and Differential Privacy

Simulates a local edge participant (e.g. Hospital A, Hospital B, Hospital C)
that trains a model locally on private data, bounds its sensitivity via
L2 clipping, and optionally perturbs the update with Gaussian Differential Privacy
using dp_filter.noise_engine before transmission.
"""

from typing import Dict, Any, Optional
import numpy as np
from dp_filter.noise_engine import clip_update, add_gaussian_noise


class FederatedClient:
    """
    Represents an edge client in the federated learning network.
    
    Attributes:
        client_id (str): Unique client identifier (e.g., 'Hospital_A').
        num_samples (int): Number of private training records held by this client.
        X (np.ndarray): Local feature matrix.
        y (np.ndarray): Local target labels.
    """

    def __init__(
        self,
        client_id: str,
        num_samples: int = 100,
        feature_dim: int = 6,
        noise_level: float = 0.1,
        random_seed: Optional[int] = None,
    ):
        self.client_id = client_id
        self.num_samples = num_samples
        self.feature_dim = feature_dim

        self.rng = np.random.RandomState(random_seed)
        rng = self.rng

        # Generate synthetic local data representing local user interaction distributions
        # True underlying relationship with client-specific bias (non-IID simulation)
        true_w = np.array([1.5, -2.0, 0.8, -1.2, 0.5, -0.3][:feature_dim])
        client_bias = rng.normal(0, 0.2, size=feature_dim)
        effective_w = true_w + client_bias

        self.X = rng.normal(0, 1.0, size=(num_samples, feature_dim))
        linear_output = np.dot(self.X, effective_w) + rng.normal(0, noise_level, size=num_samples)
        # Binary or continuous target
        self.y = 1.0 / (1.0 + np.exp(-linear_output))  # Sigmoid probabilities

    def local_train(
        self,
        global_weights: np.ndarray,
        epochs: int = 3,
        lr: float = 0.05,
    ) -> np.ndarray:
        """
        Train locally starting from global_weights using mini-batch gradient descent.
        
        Returns:
            np.ndarray: Raw model update (Delta w = w_local - w_global).
        """
        weights = global_weights.copy()

        for _ in range(epochs):
            # Compute sigmoid predictions
            preds = 1.0 / (1.0 + np.exp(-np.dot(self.X, weights)))
            # Gradient of binary cross-entropy / MSE
            gradient = np.dot(self.X.T, (preds - self.y)) / self.num_samples
            weights -= lr * gradient

        # Update vector: difference between local model and global model
        raw_update = weights - global_weights
        return raw_update

    def get_protected_update(
        self,
        global_weights: np.ndarray,
        use_dp: bool = True,
        max_norm: float = 2.0,
        epsilon: float = 1.0,
        delta: float = 1e-5,
        epochs: int = 3,
        lr: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Computes local model update and applies Differential Privacy if requested.
        
        Returns:
            dict containing client_id, num_samples, protected_update, and audit metrics.
        """
        raw_update = self.local_train(global_weights, epochs=epochs, lr=lr)
        raw_norm = float(np.linalg.norm(raw_update))

        if use_dp:
            # Apply L2 clipping and Gaussian noise via dp_filter.noise_engine
            protected_update = add_gaussian_noise(
                update=raw_update,
                max_norm=max_norm,
                epsilon=epsilon,
                delta=delta,
                rng=self.rng,
            )
            clipped_update = clip_update(raw_update, max_norm)
            clipped_norm = float(np.linalg.norm(clipped_update))
        else:
            protected_update = raw_update
            clipped_norm = raw_norm

        return {
            "client_id": self.client_id,
            "num_samples": self.num_samples,
            "update": protected_update,
            "raw_norm": raw_norm,
            "clipped_norm": clipped_norm,
            "use_dp": use_dp,
            "epsilon": epsilon if use_dp else None,
        }
