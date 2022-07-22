import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp

from hmc import HMC

class HMC_classical(HMC):
    def __init__(self, negative_log_prob, path_len=1, step_size=0.5):
        super().__init__(negative_log_prob)
        self.path_len = path_len
        self.step_size = step_size

    def dVdq(self, q):
        """
        Returns the gradient of negative log probability w.r.t. position using TFP.
        Args:
            q (list(float)): Vector location at which to take gradient.
        Returns:
            gradient (list(float)): Gradient of neg_log_prob w.r.t. position at location q.
        """
        return tfp.math.value_and_gradient(self.neg_log_prob, q)[1].numpy()

    def proposer(self, q, p):
        """
        Generates the HMC proposal using Leafrog integral.
        Args:
            q (list(float)): Vector of current position.
            p (list(float)): Vector of current momentum (usually generated from gaussian).
        Return:
            q (list(float)): New position proposal.
            p (list(float)): New momentum proposal.
        """
        q, p = np.copy(q), np.copy(p)

        p -= self.step_size * self.dVdq(q) / 2  # half step
        for _ in range(int(self.path_len / self.step_size) - 1):
            q += self.step_size * p  # whole step
            p -= self.step_size * self.dVdq(q)  # whole step
        q += self.step_size * p  # whole step
        p -= self.step_size * self.dVdq(q) / 2  # half step

        # momentum flip at end
        return q, -p