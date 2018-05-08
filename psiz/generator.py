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

"""Module for generating unjudged similarity judgment trials.

Classes:
    TrialGenerator: Base class for generating unjudged similarity
        trials.
    RandomGenerator: Concrete class for generating random similarity
        trials.
    ActiveGenerator: Concrete class for generating similarity trials
        using an active selection procedure that leverages expected
        informatin gain.

Todo:
    - implement ActiveGenerator
    - MAYBE document stimulus index formatting [0,N[
    - MAYBE take a list of trial specifications

"""

from abc import ABCMeta, abstractmethod

import numpy as np

from psiz.trials import UnjudgedTrials


class TrialGenerator(object):
    """Abstract base class for generating similarity judgment trials.

    Methods:
        generate: TODO

    Attributes:
        n_stimuli: An integer indicating the total number of unique
            stimuli.

    """

    __metaclass__ = ABCMeta

    def __init__(self, n_stimuli):
        """Initialize.

        Args:
            n_stimuli: An integer indicating the total number of unique
                stimuli.
        """
        self.n_stimuli = n_stimuli

    @abstractmethod
    def generate(self, args):
        """Return generated trials based on provided arguments.

        Args:
            n_stimuli

        Returns:
            An UnjudgedTrials object.

        """
        pass


class RandomGenerator(TrialGenerator):
    """A random similarity trial generator."""

    def __init__(self, n_stimuli):
        """Initialize.

        Args:
            n_stimuli: An integer indicating the total number of unique
                stimuli.
        """
        TrialGenerator.__init__(self, n_stimuli)

    def generate(self, n_trial, n_reference=2, n_selected=1, is_ranked=True):
        """Return generated trials based on provided arguments.

        Args:
            n_trial: TODO
            n_reference (optional): TODO
            n_selected (optional): TODO
            is_ranked (optional): TODO

        Returns:
            An UnjudgedTrials object.

        """
        n_reference = int(n_reference)
        n_selected = np.repeat(int(n_selected), n_trial)
        is_ranked = np.repeat(bool(is_ranked), n_trial)
        stimulus_set = np.empty((n_trial, n_reference + 1), dtype=np.int64)
        for i_trial in range(n_trial):
            stimulus_set[i_trial, :] = np.random.choice(
                self.n_stimuli, (1, n_reference + 1), False
            )
        # Sort indices corresponding to references.
        stimulus_set[:, 1:] = np.sort(stimulus_set[:, 1:])
        return UnjudgedTrials(
            stimulus_set, n_selected=n_selected, is_ranked=is_ranked
        )


class ActiveGenerator(TrialGenerator):
    """A trial generator that leverages expected information gain."""

    def __init__(self, n_stimuli):
        """Initialize.

        Args:
            n_stimuli:
        """
        TrialGenerator.__init__(self, n_stimuli)

    def generate(self, n_trial, n_reference=2, n_selected=1, is_ranked=True):
        """Return generated trials based on provided arguments.

        Args:
            n_trial:
            n_reference (optional):
            n_selected (optional):
            is_ranked (optional):

        Returns:
            An UnjudgedTrials object.

        """
        return None  # TODO
