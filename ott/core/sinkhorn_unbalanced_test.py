# coding=utf-8
# Copyright 2020 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""Tests for the Policy."""

from absl.testing import absltest
from absl.testing import parameterized
import jax
import jax.numpy as np
import jax.test_util

from ott.core import sinkhorn
from ott.core.ground_geometry import pointcloud


class SinkhornUnbalancedTest(jax.test_util.JaxTestCase):

  def setUp(self):
    super().setUp()
    self.rng = jax.random.PRNGKey(0)
    self.dim = 4
    self.n = 68
    self.m = 123
    self.rng, *rngs = jax.random.split(self.rng, 5)
    self.x = jax.random.uniform(rngs[0], (self.n, self.dim))
    self.y = jax.random.uniform(rngs[1], (self.m, self.dim))
    a = jax.random.uniform(rngs[2], (self.n,))
    b = jax.random.uniform(rngs[3], (self.m,))
    self.a = a / np.sum(a)
    self.b = b / np.sum(b)

  @parameterized.named_parameters(
      dict(
          testcase_name='lse-no-mom',
          lse_mode=True,
          momentum_strategy=1.0,
          inner_iterations=10,
          norm_error=1,
          tau_a=0.8,
          tau_b=0.9
          ),
      dict(
          testcase_name='lse-high-mom',
          lse_mode=True,
          momentum_strategy=1.5,
          inner_iterations=10,
          norm_error=1,
          tau_a=0.8,
          tau_b=0.9
          ),
      dict(
          testcase_name='scal-no-mom',
          lse_mode=False,
          momentum_strategy=1.0,
          inner_iterations=10,
          norm_error=1,
          tau_a=0.8,
          tau_b=0.9
          ),
      dict(
          testcase_name='scal-high-mom',
          lse_mode=False,
          momentum_strategy=1.5,
          inner_iterations=10,
          norm_error=1,
          tau_a=0.8,
          tau_b=0.9
          ))
  def test_euclidean_point_cloud(self, lse_mode, momentum_strategy,
                                 inner_iterations, norm_error, tau_a, tau_b):
    """Two point clouds, tested with various parameters."""
    threshold = 1e-3
    geom = pointcloud.PointCloudGeometry(self.x, self.y, epsilon=0.1)
    errors = sinkhorn.sinkhorn(geom, a=self.a, b=self.b,
                               threshold=threshold,
                               momentum_strategy=momentum_strategy,
                               inner_iterations=inner_iterations,
                               norm_error=norm_error,
                               lse_mode=lse_mode,
                               tau_a=tau_a,
                               tau_b=tau_b).errors
    err = errors[np.isfinite(errors)][-1]
    self.assertGreater(threshold, err)

if __name__ == '__main__':
  absltest.main()
