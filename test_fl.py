"""
test_fl.py - Unit and Integration Tests for Federated Learning & DP Integration

Tests:
1. Client local training produces valid weight updates.
2. Clipping and Gaussian noise correctly bound and perturb updates.
3. Server FedAvg correctly weights updates by sample counts.
4. Multi-round simulation runs smoothly without errors and logs history.
5. Privacy tradeoff comparison functions properly.
"""

import unittest
import numpy as np

from federated.client import FederatedClient
from federated.server import FederatedServer
from federated.simulation import run_federated_simulation, compare_dp_tradeoffs


class TestFederatedLearning(unittest.TestCase):

    def test_client_local_training(self):
        client = FederatedClient(client_id="Client_Test", num_samples=50, feature_dim=4, random_seed=42)
        global_w = np.zeros(4)
        raw_update = client.local_train(global_w, epochs=2, lr=0.1)

        self.assertEqual(raw_update.shape, (4,))
        self.assertFalse(np.all(raw_update == 0))

    def test_client_dp_protection(self):
        client = FederatedClient(client_id="Client_Test", num_samples=50, feature_dim=4, random_seed=42)
        global_w = np.zeros(4)

        # Without DP
        res_no_dp = client.get_protected_update(global_w, use_dp=False)
        self.assertFalse(res_no_dp["use_dp"])
        self.assertAlmostEqual(res_no_dp["raw_norm"], res_no_dp["clipped_norm"])

        # With DP
        max_norm = 0.5
        res_dp = client.get_protected_update(global_w, use_dp=True, max_norm=max_norm, epsilon=1.0)
        self.assertTrue(res_dp["use_dp"])
        self.assertLessEqual(res_dp["clipped_norm"], max_norm + 1e-6)
        # Verify noise was added (difference between clipped and final)
        self.assertNotEqual(res_dp["raw_norm"], float(np.linalg.norm(res_dp["update"])))

    def test_server_fedavg_aggregation(self):
        server = FederatedServer(feature_dim=3, random_seed=42)
        initial_weights = server.weights.copy()

        client_updates = [
            {"client_id": "C1", "num_samples": 100, "update": np.array([0.1, 0.2, 0.3])},
            {"client_id": "C2", "num_samples": 100, "update": np.array([0.3, 0.2, 0.1])},
        ]

        new_weights = server.aggregate_fedavg(client_updates)
        expected_update = np.array([0.2, 0.2, 0.2])  # Equal sample weights average
        np.testing.assert_allclose(new_weights, initial_weights + expected_update, rtol=1e-5)
        self.assertEqual(server.round_num, 1)
        self.assertEqual(len(server.history), 1)

    def test_full_simulation_run(self):
        sim = run_federated_simulation(rounds=3, use_dp=True, epsilon=1.0)
        self.assertEqual(sim["rounds"], 3)
        self.assertEqual(len(sim["round_history"]), 3)
        self.assertIn("final_acc", sim)
        self.assertIn("final_loss", sim)

    def test_dp_tradeoff_comparison(self):
        tradeoffs = compare_dp_tradeoffs(rounds=2)
        self.assertEqual(len(tradeoffs), 5)
        for t in tradeoffs:
            self.assertIn("final_accuracy", t)
            self.assertIn("final_loss", t)


if __name__ == "__main__":
    unittest.main(verbosity=2)
