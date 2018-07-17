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

"""Module for simulating agent behavior.

Classes:
    Agent: An object that can be initialized using a psychological
        embedding and used to simulate similarity judgments.

Todo:
    - is returned outcome_idx the best format?
    - move probability method to model module

"""
import numpy as np
from numpy.random import multinomial
import tensorflow as tf

from psiz.trials import JudgedTrials
from psiz.utils import possible_outcomes  # TODO remove?


class Agent(object):
    """Agent that simulates similarity judgments.

    Attributes:
        embedding: A PsychologicalEmbedding object that supplies a
            similarity function and embedding points.
        group_id: An integer idicating which set of attention weights
            to use when simulating judgments.
    Methods:
        simulate: Stochastically simulate similarity judgments.
        probability: Return the probability of the possible outcomes
            for each trial.

    """

    def __init__(self, embedding, group_id=0):
        """Initialize.

        Args:
            embedding: A concrete instance of a PsychologicalEmedding
                object.
            group_id (optional): If the provided embedding was inferred
                for more than one group, an index can be provided to
                indicate which set of attention weights should be used.
        """
        self.embedding = embedding
        self.group_id = group_id

    def simulate(self, trials):
        """Stochastically simulate similarity judgments.

        Args:
            trials: UnjudgedTrials object representing the
                to-be-judged trials. The order of the stimuli in the
                stimulus set is ignored for the simulations.

        Returns:
            JudgedTrials object representing the judged trials. The
                order of the stimuli is now informative.

        """
        (outcome_idx_list, prob_all) = self.probability(trials)
        # judged_trials = self._select(trials, outcome_idx_list, prob_all)
        judged_trials = self._select(trials, outcome_idx_list, prob_all)
        return judged_trials

    def probability(self, trials):
        """Return probability of outcomes for each trial.

        Args:
            trials: A set of unjudged similarity trials.

        Returns:
            outcome_idx_list: A list with one entry for each display
                configuration. Each entry contains a 2D array where
                each row contains the indices describing one outcome.
            prob_all: The probabilities associated with the different
                outcomes for each unjudged trial. In general, different
                trial configurations will have a different number of
                possible outcomes. Trials with a smaller number of
                possible outcomes are element padded with zeros to
                match the trial with the maximum number of possible
                outcomes.

        """
        n_trial_all = trials.n_trial
        n_config = trials.config_list.shape[0]
        n_dim = self.embedding.z['value'].shape[1]

        outcome_idx_list = []
        n_outcome_list = []
        max_n_outcome = 0
        for i_config in range(n_config):
            outcome_idx_list.append(
                possible_outcomes(
                    trials.config_list.iloc[i_config]
                )
            )
            n_outcome = outcome_idx_list[i_config].shape[0]
            n_outcome_list.append(n_outcome)
            if n_outcome > max_n_outcome:
                max_n_outcome = n_outcome

        prob_all = np.zeros((n_trial_all, max_n_outcome))
        for i_config in range(n_config):
            config = trials.config_list.iloc[i_config]
            outcome_idx = outcome_idx_list[i_config]
            trial_locs = trials.config_id == i_config
            n_trial = np.sum(trial_locs)
            n_outcome = n_outcome_list[i_config]
            n_reference = config['n_reference']
            n_selected_idx = config['n_selected'] - 1
            z_q = self.embedding.z['value'][
                trials.stimulus_set[trial_locs, 0], :
            ]
            z_q = np.expand_dims(z_q, axis=2)
            z_ref = np.empty((n_trial, n_dim, n_reference))
            for i_ref in range(n_reference):
                z_ref[:, :, i_ref] = \
                    self.embedding.z['value'][
                        trials.stimulus_set[trial_locs, 1+i_ref], :
                    ]

            # Precompute similarity between query and references.
            s_qref = self.embedding.similarity(
                z_q, z_ref,
                self.embedding.attention['value'][self.group_id, :]
            )

            # Compute probability of each possible outcome.
            prob = np.ones((n_trial, n_outcome), dtype=np.float64)
            for i_outcome in range(n_outcome):
                s_qref_perm = s_qref[:, outcome_idx[i_outcome, :]]
                # Start with last choice
                total = np.sum(s_qref_perm[:, n_selected_idx:], axis=1)
                # Compute sampling without replacement probability in reverse
                # order for numerical stabiltiy
                for i_selected in range(n_selected_idx, -1, -1):
                    # Grab similarity of selected reference and divide by total
                    # similarity of all available references.
                    prob[:, i_outcome] = np.multiply(
                        prob[:, i_outcome],
                        np.divide(s_qref_perm[:, i_selected], total)
                    )
                    # Add similarity for "previous" selection
                    if i_selected > 0:
                        total = total + s_qref_perm[:, i_selected-1]
            prob_all[trial_locs, 0:n_outcome] = prob

        # Correct for numerical inaccuracy.
        prob_all = np.divide(prob_all, np.sum(prob_all, axis=1, keepdims=True))
        return (outcome_idx_list, prob_all)

    def _select(self, trials, outcome_idx_list, prob_all):
        """Stochastically select from possible outcomes.

        Args:
            trials:
            outcome_idx_list:
            prob_all:


        Returns:
            A JudgedTrials object.
            The outcome index.

        """
        n_trial_all = trials.n_trial
        trial_idx_all = np.arange(n_trial_all)
        max_n_ref = trials.stimulus_set.shape[1] - 1
        n_config = trials.config_list.shape[0]

        # Pre-allocate.
        chosen_outcome_idx = np.empty((n_trial_all), dtype=np.int64)
        stimulus_set = -1 * np.ones(
            (n_trial_all, 1 + max_n_ref), dtype=np.int64
        )
        stimulus_set[:, 0] = trials.stimulus_set[:, 0]
        for i_config in range(n_config):
            n_reference = trials.config_list.iloc[i_config]['n_reference']
            outcome_idx = outcome_idx_list[i_config]
            n_outcome = outcome_idx.shape[0]
            dummy_idx = np.arange(0, n_outcome)
            trial_locs = trials.config_id == i_config
            n_trial = np.sum(trial_locs)
            trial_idx = trial_idx_all[trial_locs]
            prob = prob_all[trial_locs, 0:n_outcome]
            stimuli_set_ref = trials.stimulus_set[trial_locs, 1:]

            for i_trial in range(n_trial):
                outcome_loc = multinomial(1, prob[i_trial, :]).astype(bool)
                chosen_outcome_idx[trial_idx[i_trial]] = dummy_idx[outcome_loc]
                stimulus_set[trial_idx[i_trial], 1:n_reference+1] = \
                    stimuli_set_ref[i_trial, outcome_idx[outcome_loc, :]]

        group_id = np.full((trials.n_trial), self.group_id, dtype=np.int64)
        return JudgedTrials(
                stimulus_set,
                n_selected=trials.n_selected,
                is_ranked=trials.is_ranked, group_id=group_id
            )

    def probability_tf(self, trials, z_tf, tf_theta):
        """Return probability of outcomes for each trial.

        Args:
            trials: A set of unjudged similarity trials.
            z_tf: TensorFlow tensor representing embedding points.
            tf_theta: Dictionary of Tensorflow tensors representing
                free parameters of similarity kernel.

        Returns:
            outcome_idx_list: A list with one entry for each display
                configuration. Each entry contains a 2D array where
                each row contains the indices describing one outcome.
            prob_all: The probabilities associated with the different
                outcomes for each unjudged trial. In general, different
                trial configurations will have a different number of
                possible outcomes. Trials with a smaller number of
                possible outcomes are element padded with zeros to
                match the trial with the maximum number of possible
                outcomes.

        """
        n_trial_all = trials.n_trial
        dmy_idx = np.arange(n_trial_all)
        n_config = trials.config_list.shape[0]

        # tf_theta argument
        # # TODO can this be replaced with get exact?
        # tf_theta = {}
        # for param_name in self.embedding.theta:
        #     tf_theta[param_name] = tf.constant(
        #         self.embedding.theta[param_name]['value'], dtype=tf.float32)
        attention = self.embedding.attention['value'][0, :]  # TODO
        attention = np.expand_dims(attention, axis=0)
        attention = np.expand_dims(attention, axis=2)
        tf_attention = tf.convert_to_tensor(
            attention, dtype=tf.float32
        )

        outcome_idx_list = []
        n_outcome_list = []
        max_n_outcome = 0
        for i_config in range(n_config):
            outcome_idx_list.append(
                possible_outcomes(
                    trials.config_list.iloc[i_config]
                )
            )
            n_outcome = outcome_idx_list[i_config].shape[0]
            n_outcome_list.append(n_outcome)
            if n_outcome > max_n_outcome:
                max_n_outcome = n_outcome

        # prob_all = tf.Variable(tf.zeros((n_trial_all, max_n_outcome)), name='prob_all')
        prob_all = tf.zeros((0, max_n_outcome), dtype=tf.float32)
        indices_all = tf.zeros((0), dtype=tf.int32)
        for i_config in range(n_config):
            config = trials.config_list.iloc[i_config]
            outcome_idx = outcome_idx_list[i_config]
            trial_locs = trials.config_id == i_config
            n_trial = np.sum(trial_locs)
            n_outcome = n_outcome_list[i_config]
            n_reference = config['n_reference']
            n_selected_idx = config['n_selected'] - 1
            z_q = tf.gather(z_tf, trials.stimulus_set[trial_locs, 0])
            z_q = tf.expand_dims(z_q, axis=2)
            z_ref_list = []
            for i_ref in range(n_reference):
                z_ref_list.append(
                    tf.gather(z_tf, trials.stimulus_set[trial_locs, 1+i_ref])
                )
            z_ref = tf.stack(z_ref_list, axis=2)
            # Precompute similarity between query and references.
            s_qref = self.embedding._similarity(
                z_q, z_ref, tf_theta, tf_attention)

            # Compute probability of each possible outcome.
            # prob = tf.Variable(tf.ones((n_outcome, n_trial), dtype=np.float32), name='prob')
            prob = tf.ones((n_outcome, n_trial), dtype=np.float32)
            for i_outcome in range(n_outcome):
                s_qref_perm = tf.gather(
                    s_qref, outcome_idx[i_outcome, :], axis=1)
                # Start with last choice
                sub_sqref_perm = s_qref_perm[:, n_selected_idx:]
                total = tf.reduce_sum(sub_sqref_perm, axis=1)
                # Compute sampling without replacement probability in reverse
                # order for numerical stabiltiy
                for i_selected in range(n_selected_idx, -1, -1):
                    # Grab similarity of selected reference and divide by total
                    # similarity of all available references.
                    updates = tf.divide(s_qref_perm[:, i_selected], total)
                    split1, split2, split3 = tf.split(
                        prob, [i_outcome, 1, n_outcome-i_outcome-1], 0)
                    split2 = tf.multiply(split2, updates) # TODO maybe problem with update shape
                    prob = tf.concat((split1, split2, split3), axis=0)
                    # prob = tf.scatter_mul(prob, i_outcome, updates, name='update_prob')
                    # Add similarity for "previous" selection
                    if i_selected > 0:
                        total = total + s_qref_perm[:, i_selected-1]
            # Pad absent outcomes before putting in master prob_all.
            prob_zero = tf.zeros((max_n_outcome - n_outcome, n_trial))
            prob = tf.concat((prob, prob_zero), axis=0)
            prob = tf.transpose(prob)
            indices = dmy_idx[trial_locs]
            indices_all = tf.concat((indices_all, indices), axis=0)
            prob_all = tf.concat((prob_all, prob), axis=0)
            # prob_all = tf.scatter_add(prob_all, indices, prob)
        prob_all = tf.gather(prob_all, indices_all)

        # Correct for numerical inaccuracy.
        prob_all = tf.divide(
            prob_all, tf.reduce_sum(prob_all, axis=1, keepdims=True))
        return (outcome_idx_list, prob_all)
