# -*- coding: utf-8 -*-
# Copyright 2018 The PsiZ Authors. All Rights Reserved.
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

"""Module for testing trials.py.

Notes:
    It is critical that the function possible_outcomes returns the
        unaltered index first (as the test cases are written). Many
        downstream applications make this assumption.

Todo:
    * Test possible_outcomes attribute on instantiation and loading from
        saved file.

"""

import pytest
import numpy as np
import pandas as pd

from psiz import trials
from psiz.generator import RandomGenerator
from psiz.simulate import Agent
from psiz.models import Exponential


@pytest.fixture(scope="module")
def setup_docket_0():
    """
    """
    stimulus_set = np.array(((0, 1, 2, -1, -1, -1, -1, -1, -1),
                            (9, 12, 7, -1, -1, -1, -1, -1, -1),
                            (3, 4, 5, 6, 7, -1, -1, -1, -1),
                            (3, 4, 5, 6, 13, 14, 15, 16, 17)), dtype=np.int32)
    n_trial = 4
    n_select = np.array((1, 1, 1, 1), dtype=np.int32)
    n_reference = np.array((2, 2, 4, 8), dtype=np.int32)
    is_ranked = np.array((True, True, True, True))

    configurations = pd.DataFrame(
        {
            'n_reference': np.array([2, 4, 8], dtype=np.int32),
            'n_select': np.array([1, 1, 1], dtype=np.int32),
            'is_ranked': [True, True, True],
            'n_outcome': np.array([2, 4, 8], dtype=np.int32)
        },
        index=[0, 2, 3])
    configuration_id = np.array((0, 0, 1, 2))

    docket = trials.Docket(stimulus_set)
    return {
        'n_trial': n_trial, 'stimulus_set': stimulus_set,
        'n_reference': n_reference, 'n_select': n_select,
        'is_ranked': is_ranked, 'docket': docket,
        'configurations': configurations,
        'configuration_id': configuration_id
        }


@pytest.fixture(scope="module")
def setup_docket_1():
    """
    """
    stimulus_set = np.array(((0, 1, 2, -1, -1, -1, -1, -1, -1),
                            (9, 12, 7, -1, -1, -1, -1, -1, -1),
                            (3, 4, 5, 6, 7, -1, -1, -1, -1),
                            (3, 4, 5, 6, 13, 14, 15, 16, 17)), dtype=np.int32)
    n_trial = 4
    n_select = np.array((1, 1, 1, 2), dtype=np.int32)
    n_reference = np.array((2, 2, 4, 8), dtype=np.int32)
    is_ranked = np.array((True, True, True, True))

    configurations = pd.DataFrame(
        {
            'n_reference': np.array([2, 4, 8], dtype=np.int32),
            'n_select': np.array([1, 1, 2], dtype=np.int32),
            'is_ranked': [True, True, True],
            'n_outcome': np.array([2, 4, 56], dtype=np.int32)
        },
        index=[0, 2, 3])
    configuration_id = np.array((0, 0, 1, 2))

    docket = trials.Docket(stimulus_set, n_select=n_select)
    return {
        'n_trial': n_trial, 'stimulus_set': stimulus_set,
        'n_reference': n_reference, 'n_select': n_select,
        'is_ranked': is_ranked, 'docket': docket,
        'configurations': configurations,
        'configuration_id': configuration_id
        }


@pytest.fixture(scope="module")
def setup_obs_0():
    """
    """
    stimulus_set = np.array(((0, 1, 2, -1, -1, -1, -1, -1, -1),
                            (9, 12, 7, -1, -1, -1, -1, -1, -1),
                            (3, 4, 5, 6, 7, -1, -1, -1, -1),
                            (3, 4, 5, 6, 13, 14, 15, 16, 17)), dtype=np.int32)
    n_trial = 4
    n_select = np.array((1, 1, 1, 2), dtype=np.int32)
    n_reference = np.array((2, 2, 4, 8), dtype=np.int32)
    is_ranked = np.array((True, True, True, True))
    group_id = np.array([0, 0, 0, 0], dtype=np.int32)
    configurations = pd.DataFrame(
        {
            'n_reference': np.array([2, 4, 8], dtype=np.int32),
            'n_select': np.array([1, 1, 2], dtype=np.int32),
            'is_ranked': [True, True, True],
            'group_id': np.array([0, 0, 0], dtype=np.int32),
            'session_id': np.array([0, 0, 0], dtype=np.int32),
            'n_outcome': np.array([2, 4, 56], dtype=np.int32)
        },
        index=[0, 2, 3])
    configuration_id = np.array((0, 0, 1, 2))

    obs = trials.Observations(stimulus_set, n_select=n_select)
    return {
        'n_trial': n_trial, 'stimulus_set': stimulus_set,
        'n_reference': n_reference, 'n_select': n_select,
        'is_ranked': is_ranked, 'group_id': group_id, 'obs': obs,
        'configurations': configurations,
        'configuration_id': configuration_id
        }


@pytest.fixture(scope="module")
def setup_obs_1():
    """
    """
    stimulus_set = np.array(((0, 1, 2, -1, -1, -1, -1, -1, -1),
                            (9, 12, 7, -1, -1, -1, -1, -1, -1),
                            (3, 4, 5, 6, 7, -1, -1, -1, -1),
                            (3, 4, 5, 6, 13, 14, 15, 16, 17)), dtype=np.int32)
    n_trial = 4
    n_select = np.array((1, 1, 1, 2), dtype=np.int32)
    n_reference = np.array((2, 2, 4, 8), dtype=np.int32)
    is_ranked = np.array((True, True, True, True))
    group_id = np.array((0, 0, 1, 1), dtype=np.int32)

    configurations = pd.DataFrame(
        {
            'n_reference': np.array([2, 4, 8], dtype=np.int32),
            'n_select': np.array([1, 1, 2], dtype=np.int32),
            'is_ranked': [True, True, True],
            'group_id': np.array([0, 1, 1], dtype=np.int32),
            'session_id': np.array([0, 0, 0], dtype=np.int32),
            'n_outcome': np.array([2, 4, 56], dtype=np.int32)
        },
        index=[0, 2, 3])
    configuration_id = np.array((0, 0, 1, 2), dtype=np.int32)

    obs = trials.Observations(
        stimulus_set, n_select=n_select, group_id=group_id)
    return {
        'n_trial': n_trial, 'stimulus_set': stimulus_set,
        'n_reference': n_reference, 'n_select': n_select,
        'is_ranked': is_ranked, 'group_id': group_id, 'obs': obs,
        'configurations': configurations,
        'configuration_id': configuration_id
        }


# @pytest.fixture(scope="module")
def ground_truth(n_stimuli):
    """Return a ground truth model."""
    n_dim = 3
    n_group = 2

    model = Exponential(n_stimuli, n_dim, n_group)
    mean = np.ones((n_dim))
    cov = np.identity(n_dim)
    z = np.random.multivariate_normal(mean, cov, (n_stimuli))
    attention = np.array((
        (1.9, 1., .1),
        (.1, 1., 1.9)
    ))
    freeze_options = {
        'z': z,
        'theta': {
            'rho': 2,
            'tau': 1,
            'beta': 1,
            'gamma': 0
        },
        'phi': {
            'phi_1': attention
        }
    }
    model.freeze(freeze_options)
    return model


class TestSimilarityTrials:
    """Test functionality of base class SimilarityTrials."""

    def test_invalid_n_select(self):
        """Test handling of invalid 'n_select' argument."""
        stimulus_set = np.array((
            (0, 1, 2, -1, -1, -1, -1, -1, -1),
            (9, 12, 7, -1, -1, -1, -1, -1, -1),
            (3, 4, 5, 6, 7, -1, -1, -1, -1),
            (3, 4, 5, 6, 13, 14, 15, 16, 17)))

        # Mismatch in number of trials
        n_select = np.array((1, 1, 2))
        with pytest.raises(Exception) as e_info:
            docket = trials.Docket(stimulus_set, n_select=n_select)

        # Below support.
        n_select = np.array((1, 0, 1, 0))
        with pytest.raises(Exception) as e_info:
            docket = trials.Docket(stimulus_set, n_select=n_select)
    
        # Above support.
        n_select = np.array((2, 1, 1, 2))
        with pytest.raises(Exception) as e_info:
            docket = trials.Docket(stimulus_set, n_select=n_select)

    def test_invalid_is_ranked(self):
        """Test handling of invalid 'is_ranked' argument."""
        stimulus_set = np.array((
            (0, 1, 2, -1, -1, -1, -1, -1, -1),
            (9, 12, 7, -1, -1, -1, -1, -1, -1),
            (3, 4, 5, 6, 7, -1, -1, -1, -1),
            (3, 4, 5, 6, 13, 14, 15, 16, 17)))

        # Mismatch in number of trials
        is_ranked = np.array((True, True, True))
        with pytest.raises(Exception) as e_info:
            docket = trials.Docket(stimulus_set, is_ranked=is_ranked)

        is_ranked = np.array((True, False, True, False))
        with pytest.raises(Exception) as e_info:
            docket = trials.Docket(stimulus_set, is_ranked=is_ranked)


class TestDocket:
    """Test class Docket."""

    def test_invalid_stimulus_set(self):
        """Test handling of invalid `stimulus_set` argument."""
        # Non-integer input.
        stimulus_set = np.array((
            (0., 1, 2, -1, -1, -1, -1, -1, -1),
            (9, 12, 7, -1, -1, -1, -1, -1, -1),
            (3, 4, 5, 6, 7, -1, -1, -1, -1),
            (3, 4, 5, 6, 13, 14, 15, 16, 17)))
        with pytest.raises(Exception) as e_info:
            docket = trials.Docket(stimulus_set)

        # Contains integers below -1.
        stimulus_set = np.array((
            (0, 1, -2, -1, -1, -1, -1, -1, -1),
            (9, 12, 7, -1, -1, -1, -1, -1, -1),
            (3, 4, 5, 6, 7, -1, -1, -1, -1),
            (3, 4, 5, 6, 13, 14, 15, 16, 17)))
        with pytest.raises(Exception) as e_info:
            docket = trials.Docket(stimulus_set)

        # Does not contain enough references for each trial.
        stimulus_set = np.array((
            (0, 1, 2, -1, -1, -1, -1, -1, -1),
            (9, 12, 7, -1, -1, -1, -1, -1, -1),
            (3, 4, -1, -1, -1, -1, -1, -1, -1),
            (3, 4, 5, 6, 13, 14, 15, 16, 17)))
        with pytest.raises(Exception) as e_info:
            docket = trials.Docket(stimulus_set)

    def test_subset_config_idx(self):
        """Test if config_idx is updated correctly after subset."""
        stimulus_set = np.array((
            (0, 1, 2, -1, -1, -1, -1, -1, -1),
            (9, 12, 7, -1, -1, -1, -1, -1, -1),
            (3, 4, 5, 6, 7, -1, -1, -1, -1),
            (3, 4, 2, 6, 7, -1, -1, -1, -1),
            (3, 4, 5, 6, 13, 14, 15, 16, 17)))

        # Create original trials.
        n_select = np.array((1, 1, 1, 1, 2))
        docket = trials.Docket(stimulus_set, n_select=n_select)
        desired_config_idx = np.array((0, 0, 1, 1, 2))
        np.testing.assert_array_equal(docket.config_idx, desired_config_idx)
        # Grab subset and check that config_idx is updated to start at 0.
        trials_subset = docket.subset(np.array((2, 3, 4)))
        desired_config_idx = np.array((0, 0, 1))
        np.testing.assert_array_equal(
            trials_subset.config_idx, desired_config_idx)

    def test_stack_config_idx(self):
        """Test if config_idx is updated correctly after stack."""
        stimulus_set = np.array((
            (0, 1, 2, 3, -1, -1, -1, -1, -1),
            (9, 12, 7, 1, -1, -1, -1, -1, -1),
            (3, 4, 5, 6, 7, -1, -1, -1, -1),
            (3, 4, 2, 6, 7, -1, -1, -1, -1),
            (3, 4, 5, 6, 13, 14, 15, 16, 17)))

        # Create first set of original trials.
        n_select = np.array((1, 1, 1, 1, 1))
        trials_0 = trials.Docket(stimulus_set, n_select=n_select)
        desired_config_idx = np.array((0, 0, 1, 1, 2))
        np.testing.assert_array_equal(trials_0.config_idx, desired_config_idx)

        # Create second set of original trials, with non-overlapping
        # configuration.
        n_select = np.array((2, 2, 2, 2, 2))
        trials_1 = trials.Docket(stimulus_set, n_select=n_select)
        desired_config_idx = np.array((0, 0, 1, 1, 2))
        np.testing.assert_array_equal(trials_1.config_idx, desired_config_idx)

        # Stack trials
        trials_stack = trials.stack((trials_0, trials_1))
        desired_config_idx = np.array((0, 0, 1, 1, 2, 3, 3, 4, 4, 5))
        np.testing.assert_array_equal(
            trials_stack.config_idx, desired_config_idx)

    def test_n_trial_0(self, setup_docket_0):
        assert setup_docket_0['n_trial'] == setup_docket_0['docket'].n_trial

    def test_stimulus_set_0(self, setup_docket_0):
        np.testing.assert_array_equal(
            setup_docket_0['stimulus_set'],
            setup_docket_0['docket'].stimulus_set)

    def test_n_reference_0(self, setup_docket_0):
        np.testing.assert_array_equal(
            setup_docket_0['n_reference'], setup_docket_0['docket'].n_reference)

    def test_n_select_0(self, setup_docket_0):
        np.testing.assert_array_equal(
            setup_docket_0['n_select'], setup_docket_0['docket'].n_select)

    def test_is_ranked_0(self, setup_docket_0):
        np.testing.assert_array_equal(
            setup_docket_0['is_ranked'], setup_docket_0['docket'].is_ranked)

    def test_configurations_0(self, setup_docket_0):
        pd.testing.assert_frame_equal(
            setup_docket_0['configurations'],
            setup_docket_0['docket'].config_list)

    def test_configuration_id_0(self, setup_docket_0):
        np.testing.assert_array_equal(
            setup_docket_0['configuration_id'],
            setup_docket_0['docket'].config_idx)

    def test_n_trial_1(self, setup_docket_1):
        assert setup_docket_1['n_trial'] == setup_docket_1['docket'].n_trial

    def test_stimulus_set_1(self, setup_docket_1):
        np.testing.assert_array_equal(
            setup_docket_1['stimulus_set'], setup_docket_1['docket'].stimulus_set)

    def test_n_reference_1(self, setup_docket_1):
        np.testing.assert_array_equal(
            setup_docket_1['n_reference'], setup_docket_1['docket'].n_reference)

    def test_n_select_1(self, setup_docket_1):
        np.testing.assert_array_equal(
            setup_docket_1['n_select'], setup_docket_1['docket'].n_select)

    def test_is_ranked_1(self, setup_docket_1):
        np.testing.assert_array_equal(
            setup_docket_1['is_ranked'], setup_docket_1['docket'].is_ranked)

    def test_configurations_1(self, setup_docket_1):
        pd.testing.assert_frame_equal(
            setup_docket_1['configurations'],
            setup_docket_1['docket'].config_list)

    def test_configuration_id_1(self, setup_docket_1):
        np.testing.assert_array_equal(
            setup_docket_1['configuration_id'],
            setup_docket_1['docket'].config_idx)

    def test_save_load_file(self, setup_docket_0, tmpdir):
        """Test saving and loading of Docket."""
        # Save docket.
        fn = tmpdir.join('docket_test.hdf5')
        setup_docket_0['docket'].save(fn)
        # Load the saved docket.
        loaded_docket = trials.load_trials(fn)
        # Check that the loaded Docket object is correct.
        assert setup_docket_0['n_trial'] == loaded_docket.n_trial
        np.testing.assert_array_equal(
            setup_docket_0['stimulus_set'], loaded_docket.stimulus_set)
        np.testing.assert_array_equal(
            setup_docket_0['n_reference'], loaded_docket.n_reference)
        np.testing.assert_array_equal(
            setup_docket_0['n_select'], loaded_docket.n_select)
        np.testing.assert_array_equal(
            setup_docket_0['is_ranked'], loaded_docket.is_ranked)
        pd.testing.assert_frame_equal(
            setup_docket_0['configurations'],
            loaded_docket.config_list)
        np.testing.assert_array_equal(
            setup_docket_0['configuration_id'],
            loaded_docket.config_idx)
        # TODO test possible_outcomes


class TestObservations:
    """Test class Observations."""

    def test_invalid_stimulus_set(self):
        """Test handling of invalid `stimulus_set` argument."""
        # Non-integer input.
        stimulus_set = np.array((
            (0., 1, 2, -1, -1, -1, -1, -1, -1),
            (9, 12, 7, -1, -1, -1, -1, -1, -1),
            (3, 4, 5, 6, 7, -1, -1, -1, -1),
            (3, 4, 5, 6, 13, 14, 15, 16, 17)))
        with pytest.raises(Exception) as e_info:
            obs = trials.Observations(stimulus_set)

        # Contains integers below -1.
        stimulus_set = np.array((
            (0, 1, -2, -1, -1, -1, -1, -1, -1),
            (9, 12, 7, -1, -1, -1, -1, -1, -1),
            (3, 4, 5, 6, 7, -1, -1, -1, -1),
            (3, 4, 5, 6, 13, 14, 15, 16, 17)))
        with pytest.raises(Exception) as e_info:
            obs = trials.Observations(stimulus_set)

        # Does not contain enough references for each trial.
        stimulus_set = np.array((
            (0, 1, 2, -1, -1, -1, -1, -1, -1),
            (9, 12, 7, -1, -1, -1, -1, -1, -1),
            (3, 4, -1, -1, -1, -1, -1, -1, -1),
            (3, 4, 5, 6, 13, 14, 15, 16, 17)))
        with pytest.raises(Exception) as e_info:
            obs = trials.Observations(stimulus_set)

    def test_invalid_group_id(self):
        """Test handling of invalid `group_id` argument."""
        stimulus_set = np.array((
            (0, 1, 2, -1, -1, -1, -1, -1, -1),
            (9, 12, 7, -1, -1, -1, -1, -1, -1),
            (3, 4, 5, 6, 7, -1, -1, -1, -1),
            (3, 4, 5, 6, 13, 14, 15, 16, 17)))

        # Mismatch in number of trials
        group_id = np.array((0, 0, 1))
        with pytest.raises(Exception) as e_info:
            obs = trials.Observations(stimulus_set, group_id=group_id)

        # Below support.
        group_id = np.array((0, -1, 1, 0))
        with pytest.raises(Exception) as e_info:
            obs = trials.Observations(stimulus_set, group_id=group_id)

    def test_subset_config_idx(self):
        """Test if config_idx is updated correctly after subset."""
        stimulus_set = np.array((
            (0, 1, 2, -1, -1, -1, -1, -1, -1),
            (9, 12, 7, -1, -1, -1, -1, -1, -1),
            (3, 4, 5, 6, 7, -1, -1, -1, -1),
            (3, 4, 2, 6, 7, -1, -1, -1, -1),
            (3, 4, 5, 6, 13, 14, 15, 16, 17)))

        # Create original trials.
        n_select = np.array((1, 1, 1, 1, 2))
        obs = trials.Observations(stimulus_set, n_select=n_select)
        desired_config_idx = np.array((0, 0, 1, 1, 2))
        np.testing.assert_array_equal(obs.config_idx, desired_config_idx)
        # Grab subset and check that config_idx is updated to start at 0.
        trials_subset = obs.subset(np.array((2, 3, 4)))
        desired_config_idx = np.array((0, 0, 1))
        np.testing.assert_array_equal(
            trials_subset.config_idx, desired_config_idx)

    def test_stack_config_idx(self):
        """Test if config_idx is updated correctly after stack."""
        stimulus_set = np.array((
            (0, 1, 2, 3, -1, -1, -1, -1, -1),
            (9, 12, 7, 1, -1, -1, -1, -1, -1),
            (3, 4, 5, 6, 7, -1, -1, -1, -1),
            (3, 4, 2, 6, 7, -1, -1, -1, -1),
            (3, 4, 5, 6, 13, 14, 15, 16, 17)))

        # Create first set of original trials.
        n_select = np.array((1, 1, 1, 1, 1))
        trials_0 = trials.Observations(stimulus_set, n_select=n_select)
        desired_config_idx = np.array((0, 0, 1, 1, 2))
        np.testing.assert_array_equal(trials_0.config_idx, desired_config_idx)

        # Create second set of original trials, with non-overlapping
        # configuration.
        n_select = np.array((2, 2, 2, 2, 2))
        trials_1 = trials.Observations(stimulus_set, n_select=n_select)
        desired_config_idx = np.array((0, 0, 1, 1, 2))
        np.testing.assert_array_equal(trials_1.config_idx, desired_config_idx)

        # Stack trials
        trials_stack = trials.stack((trials_0, trials_1))
        desired_config_idx = np.array((0, 0, 1, 1, 2, 3, 3, 4, 4, 5))
        np.testing.assert_array_equal(
            trials_stack.config_idx, desired_config_idx)

    def test_n_trial_0(self, setup_obs_0):
        assert setup_obs_0['n_trial'] == setup_obs_0['obs'].n_trial

    def test_stimulus_set_0(self, setup_obs_0):
        np.testing.assert_array_equal(
            setup_obs_0['stimulus_set'], setup_obs_0['obs'].stimulus_set)

    def test_n_reference_0(self, setup_obs_0):
        np.testing.assert_array_equal(
            setup_obs_0['n_reference'], setup_obs_0['obs'].n_reference)

    def test_n_select_0(self, setup_obs_0):
        np.testing.assert_array_equal(
            setup_obs_0['n_select'], setup_obs_0['obs'].n_select)

    def test_is_ranked_0(self, setup_obs_0):
        np.testing.assert_array_equal(
            setup_obs_0['is_ranked'], setup_obs_0['obs'].is_ranked)

    def test_configurations_0(self, setup_obs_0):
        pd.testing.assert_frame_equal(
            setup_obs_0['configurations'],
            setup_obs_0['obs'].config_list)

    def test_configuration_id_0(self, setup_obs_0):
        np.testing.assert_array_equal(
            setup_obs_0['configuration_id'],
            setup_obs_0['obs'].config_idx)

    def test_n_trial_1(self, setup_obs_1):
        assert setup_obs_1['n_trial'] == setup_obs_1['obs'].n_trial

    def test_stimulus_set_1(self, setup_obs_1):
        np.testing.assert_array_equal(
            setup_obs_1['stimulus_set'], setup_obs_1['obs'].stimulus_set)

    def test_n_reference_1(self, setup_obs_1):
        np.testing.assert_array_equal(
            setup_obs_1['n_reference'], setup_obs_1['obs'].n_reference)

    def test_n_select_1(self, setup_obs_1):
        np.testing.assert_array_equal(
            setup_obs_1['n_select'], setup_obs_1['obs'].n_select)

    def test_is_ranked_1(self, setup_obs_1):
        np.testing.assert_array_equal(
            setup_obs_1['is_ranked'], setup_obs_1['obs'].is_ranked)

    def test_configurations_1(self, setup_obs_1):
        pd.testing.assert_frame_equal(
            setup_obs_1['configurations'],
            setup_obs_1['obs'].config_list)

    def test_configuration_id_1(self, setup_obs_1):
        np.testing.assert_array_equal(
            setup_obs_1['configuration_id'],
            setup_obs_1['obs'].config_idx
        )

    def test_set_group_id(self, setup_obs_1):
        obs = setup_obs_1['obs']
        # Test initial configuration.
        np.testing.assert_array_equal(
            setup_obs_1['group_id'], obs.group_id)
        # Test setting group_id using scalar.
        new_group_id_0 = 3
        obs.set_group_id(new_group_id_0)
        expected_group_id_0 = np.array((3, 3, 3, 3), dtype=np.int32)
        np.testing.assert_array_equal(expected_group_id_0, obs.group_id)
        # Test setting group_id using correct-sized array.
        new_group_id_1 = np.array((1, 1, 2, 2), dtype=np.int32)
        obs.set_group_id(new_group_id_1)
        expected_group_id_1 = np.array((1, 1, 2, 2), dtype=np.int32)
        np.testing.assert_array_equal(expected_group_id_1, obs.group_id)
        # Test setting group_id using incorrect-sized array.
        new_group_id_2 = np.array((1, 1, 2), dtype=np.int32)
        with pytest.raises(Exception) as e_info:
            obs.set_group_id(new_group_id_2)

    def test_save_load_file(self, setup_obs_0, tmpdir):
        """Test saving and loading of Observations."""
        # Save observations.
        fn = tmpdir.join('obs_test.hdf5')
        setup_obs_0['obs'].save(fn)
        # Load the saved observations.
        loaded_obs = trials.load_trials(fn)
        # Check that the loaded Observations object is correct.
        assert setup_obs_0['n_trial'] == loaded_obs.n_trial
        np.testing.assert_array_equal(
            setup_obs_0['stimulus_set'], loaded_obs.stimulus_set)
        np.testing.assert_array_equal(
            setup_obs_0['n_reference'], loaded_obs.n_reference)
        np.testing.assert_array_equal(
            setup_obs_0['n_select'], loaded_obs.n_select)
        np.testing.assert_array_equal(
            setup_obs_0['is_ranked'], loaded_obs.is_ranked)
        np.testing.assert_array_equal(
            setup_obs_0['group_id'], loaded_obs.group_id)
        pd.testing.assert_frame_equal(
            setup_obs_0['configurations'],
            loaded_obs.config_list)
        np.testing.assert_array_equal(
            setup_obs_0['configuration_id'],
            loaded_obs.config_idx)
        # TODO test possible_outcomes


class TestStack:
    """Test stack static method."""

    def test_stack_same_config(self):
        n_stimuli = 10
        model_truth = ground_truth(n_stimuli)

        n_trial = 50
        n_reference = 8
        n_select = 2
        generator = RandomGenerator(n_stimuli)
        docket = generator.generate(n_trial, n_reference, n_select)

        double_trials = trials.stack((docket, docket))

        assert double_trials.n_trial == 2 * n_trial
        np.testing.assert_array_equal(
            double_trials.n_reference[0:n_trial], docket.n_reference)
        np.testing.assert_array_equal(
            double_trials.n_reference[n_trial:], docket.n_reference)

        np.testing.assert_array_equal(
            double_trials.n_select[0:n_trial], docket.n_select)
        np.testing.assert_array_equal(
            double_trials.n_select[n_trial:], docket.n_select)

        np.testing.assert_array_equal(
            double_trials.is_ranked[0:n_trial], docket.is_ranked)
        np.testing.assert_array_equal(
            double_trials.is_ranked[n_trial:], docket.is_ranked)

        agent_novice = Agent(model_truth, group_id=0)
        agent_expert = Agent(model_truth, group_id=1)
        obs_novice = agent_novice.simulate(docket)
        obs_expert = agent_expert.simulate(docket)
        obs_all = trials.stack((obs_novice, obs_expert))

        assert obs_all.n_trial == 2 * n_trial
        np.testing.assert_array_equal(
            obs_all.n_reference[0:n_trial], obs_novice.n_reference)
        np.testing.assert_array_equal(
            obs_all.n_reference[n_trial:], obs_expert.n_reference)

        np.testing.assert_array_equal(
            obs_all.n_select[0:n_trial], obs_novice.n_select)
        np.testing.assert_array_equal(
            obs_all.n_select[n_trial:], obs_expert.n_select)

        np.testing.assert_array_equal(
            obs_all.is_ranked[0:n_trial], obs_novice.is_ranked)
        np.testing.assert_array_equal(
            obs_all.is_ranked[n_trial:], obs_expert.is_ranked)

        np.testing.assert_array_equal(
            obs_all.group_id[0:n_trial], obs_novice.group_id)
        np.testing.assert_array_equal(
            obs_all.group_id[n_trial:], obs_expert.group_id)

    def test_stack_different_config(self):
        """Test stack static method with different configurations."""
        n_stimuli = 20
        generator = RandomGenerator(n_stimuli)

        n_reference1 = 2
        n_select1 = 1
        trials1 = generator.generate(5, n_reference1, n_select1)

        n_reference2 = 4
        n_select2 = 2
        trials2 = generator.generate(5, n_reference2, n_select2)

        n_reference3 = 6
        n_select3 = 2
        trials3 = generator.generate(5, n_reference3, n_select3)

        trials_all = trials.stack((trials1, trials2, trials3))

        desired_n_reference = np.hstack((
            n_reference1 * np.ones((5), dtype=np.int32),
            n_reference2 * np.ones((5), dtype=np.int32),
            n_reference3 * np.ones((5), dtype=np.int32),
        ))

        np.testing.assert_array_equal(
            trials_all.n_reference, desired_n_reference
        )

    def test_padding(self):
        """Test padding values when using stack and subset method."""
        n_stimuli = 20
        generator = RandomGenerator(n_stimuli)

        n_reference1 = 2
        n_select1 = 1
        trials1 = generator.generate(5, n_reference1, n_select1)

        n_reference2 = 4
        n_select2 = 2
        trials2 = generator.generate(5, n_reference2, n_select2)

        n_reference3 = 8
        n_select3 = 2
        trials3 = generator.generate(5, n_reference3, n_select3)

        trials_all = trials.stack((trials1, trials2, trials3))

        # Check padding values of first set (non-padded and then padded
        # values).
        assert np.sum(np.equal(trials_all.stimulus_set[1:5, 0:3], -1)) == 0
        np.testing.assert_array_equal(
            trials_all.stimulus_set[0:5, 3:],
            -1 * np.ones((5, 6), dtype=np.int32)
        )
        # Check padding values of second set (non-padded and then padded
        # values).
        assert np.sum(np.equal(trials_all.stimulus_set[5:10, 0:5], -1)) == 0
        np.testing.assert_array_equal(
            trials_all.stimulus_set[5:10, 5:],
            -1 * np.ones((5, 4), dtype=np.int32)
        )
        # Check padding values of third set (non-padded and then padded
        # values).
        assert np.sum(np.equal(trials_all.stimulus_set[10:15, :], -1)) == 0

        # Check padding when taking subset.
        trials_subset = trials_all.subset(np.arange(10))
        assert trials_subset.stimulus_set.shape[1] == 5
        # Check padding values of first set (non-padded and then padded
        # values).
        assert np.sum(np.equal(trials_subset.stimulus_set[1:5, 0:3], -1)) == 0
        np.testing.assert_array_equal(
            trials_subset.stimulus_set[0:5, 3:],
            -1 * np.ones((5, 2), dtype=np.int32)
        )
        # Check padding values of second set (non-padded and then padded
        # values).
        assert np.sum(np.equal(trials_subset.stimulus_set[5:10, 0:5], -1)) == 0


class TestPossibleOutcomes:
    """Test possible outcomes."""

    def test_possible_outcomes_2c1(self):
        """Test outcomes 2 choose 1 ranked trial."""
        stimulus_set = np.array(((0, 1, 2), (9, 12, 7)))
        n_select = 1 * np.ones((2))
        tasks = trials.Docket(stimulus_set, n_select=n_select)

        po = trials.possible_outcomes(tasks.config_list.iloc[0])

        correct = np.array(((0, 1), (1, 0)))
        np.testing.assert_array_equal(po, correct)

    def test_possible_outcomes_3c2(self):
        """Test outcomes 3 choose 2 ranked trial."""
        stimulus_set = np.array(((0, 1, 2, 3), (33, 9, 12, 7)))
        n_select = 2 * np.ones((2))
        tasks = trials.Docket(stimulus_set, n_select=n_select)

        po = trials.possible_outcomes(tasks.config_list.iloc[0])

        correct = np.array((
            (0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0),
            (2, 0, 1), (2, 1, 0)))
        np.testing.assert_array_equal(po, correct)

    def test_possible_outcomes_4c2(self):
        """Test outcomes 4 choose 2 ranked trial."""
        stimulus_set = np.array(((0, 1, 2, 3, 4), (45, 33, 9, 12, 7)))
        n_select = 2 * np.ones((2))
        tasks = trials.Docket(stimulus_set, n_select=n_select)

        po = trials.possible_outcomes(tasks.config_list.iloc[0])

        correct = np.array((
            (0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2),
            (1, 0, 2, 3), (1, 2, 0, 3), (1, 3, 0, 2),
            (2, 0, 1, 3), (2, 1, 0, 3), (2, 3, 0, 1),
            (3, 0, 1, 2), (3, 1, 0, 2), (3, 2, 0, 1)))
        np.testing.assert_array_equal(po, correct)

    def test_possible_outcomes_8c1(self):
        """Test outcomes 8 choose 1 ranked trial."""
        stimulus_set = np.array((
            (0, 1, 2, 3, 4, 5, 6, 7, 8),
            (45, 33, 9, 12, 7, 2, 5, 4, 3)))
        n_select = 1 * np.ones((2))
        tasks = trials.Docket(stimulus_set, n_select=n_select)

        po = trials.possible_outcomes(tasks.config_list.iloc[0])

        correct = np.array((
            (0, 1, 2, 3, 4, 5, 6, 7),
            (1, 0, 2, 3, 4, 5, 6, 7),
            (2, 0, 1, 3, 4, 5, 6, 7),
            (3, 0, 1, 2, 4, 5, 6, 7),
            (4, 0, 1, 2, 3, 5, 6, 7),
            (5, 0, 1, 2, 3, 4, 6, 7),
            (6, 0, 1, 2, 3, 4, 5, 7),
            (7, 0, 1, 2, 3, 4, 5, 6)))
        np.testing.assert_array_equal(po, correct)
