# -*- coding: utf-8 -*-
# Copyright 2019 The PsiZ Authors. All Rights Reserved.
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
# ==============================================================================

"""Module for testing generator.py.

Todo:
    - test ActiveGenerator
    - more information gain tests
"""

import numpy as np
import pytest

from psiz import generator
from psiz.models import Exponential
from psiz.trials import stack, Docket
from psiz.simulate import Agent


@pytest.fixture(scope="module")
def ground_truth():
    """Return a ground truth embedding."""
    n_stimuli = 10
    n_dim = 2

    model = Exponential(n_stimuli)
    mean = np.zeros((n_dim))
    cov = .1 * np.identity(n_dim)
    z = np.random.multivariate_normal(mean, cov, (n_stimuli))
    freeze_options = {
        'z': z,
        'theta': {
            'rho': 2,
            'tau': 1,
            'beta': 10,
            'gamma': 0
        }
    }
    model.freeze(freeze_options)
    return model


def simulated_samples(z):
    """Simulate posterior samples for a set of embedding points."""
    n_stimuli = z.shape[0]
    n_dim = z.shape[1]
    n_sample = 1000

    stim_cov = np.array((.08, .01, .01, .01, .01, .01, .01, .01, .01, .01))
    # Draw samples
    z_samples = np.empty((n_sample, n_stimuli, n_dim))
    for i_stimulus in range(n_stimuli):
        z_samples[:, i_stimulus, :] = np.random.multivariate_normal(
            z[i_stimulus], stim_cov[i_stimulus] * np.identity(n_dim),
            (n_sample)
        )
    z_samples = np.transpose(z_samples, axes=[1, 2, 0])
    return {'z': z_samples}


def test_random_generator():
    """Test random generator."""
    n_stimuli_desired = 10
    n_trial_desired = 50
    n_reference_desired = 4
    n_select_desired = 2
    is_ranked_desired = True
    gen = generator.RandomGenerator(
        n_reference=n_reference_desired,
        n_select=n_select_desired)
    docket = gen.generate(n_trial_desired, n_stimuli_desired)

    assert docket.n_trial == n_trial_desired
    assert sum(docket.n_reference == n_reference_desired) == n_trial_desired
    assert docket.stimulus_set.shape[0] == n_trial_desired
    assert docket.stimulus_set.shape[1] == n_reference_desired + 1
    min_actual = np.min(docket.stimulus_set)
    max_actual = np.max(docket.stimulus_set)
    assert min_actual >= -1  # Need -1 for padding.
    assert max_actual < n_stimuli_desired
    n_unique_desired = n_reference_desired + 1
    for i_trial in range(n_trial_desired):
        # NOTE: The padding padding values (-1)'s are counted as unique, thus
        # the indexing into stimulus set.
        assert (
            len(np.unique(
                docket.stimulus_set[i_trial, 0:n_reference_desired+1])
                ) == n_unique_desired
        )
    assert sum(docket.n_select == n_select_desired) == n_trial_desired
    assert sum(docket.is_ranked == is_ranked_desired) == n_trial_desired


def test_information_gain(ground_truth):
    """Test expected information gain computation."""
    z = ground_truth.z['value']
    samples = simulated_samples(z)

    gen = generator.ActiveGenerator()
    docket_0 = Docket(
        np.array([[0, 1, 2]], dtype=np.int32),
        np.array([1], dtype=np.int32)
        )
    docket_1 = Docket(
        np.array([[3, 1, 2]], dtype=np.int32),
        np.array([1], dtype=np.int32)
        )
    # Compute expected informatin gain.
    ig_0 = generator.information_gain(ground_truth, samples, docket_0)
    ig_1 = generator.information_gain(ground_truth, samples, docket_1)

    assert ig_0 > ig_1

    # Check case for multiple candidate trials.
    docket_01 = Docket(
        np.array([[0, 1, 2], [3, 1, 2]], dtype=np.int32),
        np.array([1, 1], dtype=np.int32)
        )
    ig_01 = generator.information_gain(ground_truth, samples, docket_01)
    assert ig_01[0] == ig_0
    assert ig_01[1] == ig_1

    # Check case for multiple candidate trials with different configurations.
    docket_23 = Docket(
        np.array([[0, 1, 2, 4, 9], [3, 1, 5, 6, 8]], dtype=np.int32),
        np.array([2, 2], dtype=np.int32)
        )
    ig_23 = generator.information_gain(ground_truth, samples, docket_23)

    docket_0123 = Docket(
        np.array([
            [0, 1, 2, -1, -1],
            [3, 1, 2, -1, -1],
            [0, 1, 2, 4, 9],
            [3, 1, 5, 6, 8]
        ], dtype=np.int32),
        np.array([1, 1, 2, 2], dtype=np.int32)
        )
    ig_0123 = generator.information_gain(
        ground_truth, samples, docket_0123)
    assert ig_0123[0] == ig_0
    assert ig_0123[1] == ig_1
    assert ig_0123[2] == ig_23[0]
    assert ig_0123[3] == ig_23[1]


def test_kl_divergence():
    """Test computation of KL divergence."""
    mu_left = np.array([0, 0])
    mu_right = np.array([10, 0])

    cov_sm = np.eye(2)
    cov_lg = 10 * np.eye(2)

    kl_sm_sm = generator.normal_kl_divergence(
        mu_left, cov_sm, mu_right, cov_sm)
    kl_sm_lg = generator.normal_kl_divergence(
        mu_left, cov_sm, mu_right, cov_lg)
    kl_lg_sm = generator.normal_kl_divergence(
        mu_left, cov_lg, mu_right, cov_sm)
    kl_lg_lg = generator.normal_kl_divergence(
        mu_left, cov_lg, mu_right, cov_lg)

    np.testing.assert_almost_equal(kl_sm_sm, 50.00000, decimal=5)
    np.testing.assert_almost_equal(kl_sm_lg, 6.402585, decimal=5)
    np.testing.assert_almost_equal(kl_lg_sm, 56.697415, decimal=5)
    np.testing.assert_almost_equal(kl_lg_lg, 5.000000, decimal=5)

# @pytest.fixture(scope="module")
# def unbalanced_trials():
#     """Return a set of unbalanced trials.

#     In this context, unbalanced means trials in which a stimulus
#     occurs rarely.
#     """

#     n_stimuli_desired = 9
#     n_trial_desired = 200
#     n_reference_desired = 2
#     n_select_desired = 1
#     gen = generator.RandomGenerator(
#         n_reference=n_reference_desired,
#         n_select=n_select_desired)
#     unjudged_trials_0 = gen.generate(
#         n_trial_desired, n_stimuli_desired)
#     n_stimuli_desired = 10
#     n_trial_desired = 50
#     gen = generator.RandomGenerator(
#         n_reference=n_reference_desired,
#         n_select=n_select_desired)
#     unjudged_trials_1 = gen.generate(
#         n_trial_desired, n_stimuli_desired)
#     unjudged_trials = stack((unjudged_trials_0, unjudged_trials_1))
#     return unjudged_trials
