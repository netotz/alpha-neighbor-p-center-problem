import numpy as np


class ReactiveBeta:
    """
    Reactive GRASP class.
    """

    def __init__(self, betas_count: int = 11, seed: int | None = None):
        """
        `betas_count`: Number of beta values to consider.

        `seed`: Seed for random number generator.
        """
        self.betas = np.linspace(0, 1, betas_count, dtype=np.half)
        self.indexes: dict[float, int] = {b: i for i, b in np.ndenumerate(self.betas)}

        self.probabilities = np.full(betas_count, 1 / betas_count, np.single)
        self.counts = np.zeros(betas_count, np.intc)
        self.means = np.zeros(betas_count, dtype=np.double)

        self.rng = np.random.default_rng(seed)

    def choose(self) -> float:
        """
        Returns a random beta value according to the probability distribution.
        """
        return self.rng.choice(self.betas, p=self.probabilities)

    def increment(self, beta: float, obj_func: int) -> None:
        """
        Increments the count of `beta` and updates its running mean.
        """
        i = self.indexes[beta]
        self.counts[i] += 1
        self.means[i] = self.means[i] + ((obj_func - self.means[i]) / self.counts[i])

    def update(self, best_obj_func: int) -> None:
        """
        Updates the probability distribution of the beta values.
        """
        # get mean of means for betas that haven't been chosen
        global_mean = self.means[self.means.nonzero()].mean()

        qs = np.zeros(self.probabilities.size, np.single)
        qsum = 0
        for i in range(self.betas.size):
            qs[i] = qi = best_obj_func / (
                global_mean if self.means[i] == 0 else self.means[i]
            )
            qsum += qi

        self.probabilities = qs / qsum
