import numpy as np


def clip_update(update, max_norm):
    """
    Clip a model update so its L2 norm
    does not exceed max_norm.
    """

    norm = np.linalg.norm(update)

    if norm > max_norm:
        update = update * (max_norm / norm)

    return update


def add_gaussian_noise(update, max_norm, epsilon, delta, rng=None):
    """
    Apply Gaussian Differential Privacy
    to a model update.
    """

    # Clip the update first
    clipped_update = clip_update(update, max_norm)

    # Calculate noise scale
    sensitivity = max_norm

    sigma = (
        sensitivity
        * np.sqrt(2 * np.log(1.25 / delta))
        / epsilon
    )

    generator = rng if rng is not None else np.random
    noise = generator.normal(
        0,
        sigma,
        size=clipped_update.shape
    )

    private_update = clipped_update + noise
    return private_update
