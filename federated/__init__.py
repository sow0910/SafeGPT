"""
federated - Privacy-Preserving Federated Learning Module for SafeGPT

Integrates local client model updates with Differential Privacy (dp_filter)
and centralized Federated Averaging (FedAvg).
"""

from .client import FederatedClient
from .server import FederatedServer
from .simulation import run_federated_simulation

__all__ = ["FederatedClient", "FederatedServer", "run_federated_simulation"]
