import numpy as np

from dp_filter.noise_engine import (
    clip_update,
    add_gaussian_noise
)


# Example model update
update = np.array([2.0, 4.0, 6.0, 8.0])


print("\n========== ORIGINAL UPDATE ==========")
print(update)


# Clip the update
clipped = clip_update(update, max_norm=5.0)

print("\n========== CLIPPED UPDATE ==========")
print(clipped)


# Apply Differential Privacy
private_update = add_gaussian_noise(
    update,
    max_norm=5.0,
    epsilon=1.0,
    delta=1e-5
)

print("\n========== DP PROTECTED UPDATE ==========")
print(private_update)
