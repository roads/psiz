# -*- coding: utf-8 -*-
# Copyright 2020 The PsiZ Authors. All Rights Reserved.
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

"""Example script that samples from the posterior of an embedding.

Synthetic data is generated from a ground truth embedding model. For
simplicity, the ground truth model is also used as the inferred
model in this example. In practice, the judged trials would be used to
infer a separate embedding model since the ground truth is not known.
In this example, using the ground truth allows us to see how the
posterior sampling algorithm works under ideal conditions. Posterior
samples are drawn with increasing amounts of data, allowing one to see
how the posterior changes as the amount of data increases.

Notes:
    This script takes approximately 20 minutes to execute on a modern
        machine and will save the video as a file called
        `posterior_evolution.mp4`.

"""

import copy

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from psiz.generator import RandomGenerator
import psiz.models
from psiz.simulate import Agent
from psiz.utils import similarity_matrix, matrix_comparison


def main():
    """Run script."""
    # Settings
    n_trial = 2500
    n_frame = 20
    n_sample = 1000
    n_burn = 100
    thin_step = 3

    # Ground truth model.
    emb_true = ground_truth()
    n_stimuli = emb_true.z.shape[0]
    n_dim = emb_true.z.shape[1]
    z_true = emb_true.z.astype(np.float64)
    simmat_true = similarity_matrix(
        emb_true.similarity, emb_true.z)

    # Generate a random docket of trials.
    n_reference = 2
    n_select = 1
    generator = RandomGenerator(
        emb_true.n_stimuli, n_reference=n_reference, n_select=n_select
    )
    docket = generator.generate(n_trial)

    # Simulate similarity judgments using ground truth model.
    agent = Agent(emb_true)
    obs = agent.simulate(docket)

    # Use the ground-truth embedding model.
    emb_inferred = emb_true
    z_original = copy.copy(emb_inferred.z)

    z_samp_list = n_frame * [None]
    z_central_list = n_frame * [None]
    r2_list = n_frame * [None]
    n_obs = np.floor(np.linspace(20, n_trial, n_frame)).astype(np.int64)
    for i_frame in range(n_frame):
        include_idx = np.arange(0, n_obs[i_frame])
        samples = emb_inferred.posterior_samples(
            obs.subset(include_idx), n_sample, n_burn, thin_step)
        z_samp = samples['z']
        z_central = np.median(z_samp, axis=2)
        z_samp = np.transpose(z_samp, axes=[2, 0, 1])
        z_samp_list[i_frame] = np.reshape(
            z_samp, (n_sample * n_stimuli, n_dim))
        z_central_list[i_frame] = z_central

        emb_inferred.z = z_central
        simmat_infer = similarity_matrix(
            emb_inferred.similarity, emb_inferred.z)
        r2 = matrix_comparison(
            simmat_infer, simmat_true, score='r2'
        )
        r2_list[i_frame] = r2
        print('    Frame: {0} | r^2: {1: >6.2f}'.format(i_frame, r2))
        emb_inferred.z = z_original

    cmap = matplotlib.cm.get_cmap('jet')
    norm = matplotlib.colors.Normalize(vmin=0., vmax=emb_true.n_stimuli)
    color_array = cmap(norm(range(emb_true.n_stimuli)))
    color_array_samp = np.tile(color_array, (n_sample, 1))

    # Set up formatting for the movie files
    Writer = animation.writers['ffmpeg']
    metadata = dict(
            title='Embedding Inference Evolution', artist='Matplotlib')
    writer = Writer(fps=3, metadata=metadata)

    # Initialize first frame.
    i_frame = 0

    fig = plt.figure(figsize=(5.5, 2), dpi=200)

    ax1 = fig.add_subplot(1, 3, 1)
    ax1.scatter(
        z_true[:, 0], z_true[:, 1], s=15, c=color_array, marker='o')
    ax1.set_title('Ground Truth')
    ax1.set_aspect('equal')
    ax1.set_xlim(-.05, .55)
    ax1.set_xticks([])
    ax1.set_ylim(-.05, .55)
    ax1.set_yticks([])

    ax2 = fig.add_subplot(1, 3, 2)
    scat2 = ax2.scatter(
        z_central_list[i_frame][:, 0], z_central_list[i_frame][:, 1],
        s=15, c=color_array, marker='X')
    ax2.set_title('Point Estimate')
    ax2.set_aspect('equal')
    ax2.set_xlim(-.05, .55)
    ax2.set_xticks([])
    ax2.set_ylim(-.05, .55)
    ax2.set_yticks([])

    ax3 = fig.add_subplot(1, 3, 3)
    scat3 = ax3.scatter(
        z_samp_list[i_frame][:, 0], z_samp_list[i_frame][:, 1],
        s=5, c=color_array_samp, alpha=.01, edgecolors='none')
    ax3.set_title('Posterior Estimate')
    ax3.set_aspect('equal')
    ax3.set_xlim(-.05, .55)
    ax3.set_xticks([])
    ax3.set_ylim(-.05, .55)
    ax3.set_yticks([])

    def update(frame_number):
        scat2.set_offsets(
            z_central_list[frame_number])
        scat3.set_offsets(
            z_samp_list[frame_number])
    ani = animation.FuncAnimation(fig, update, frames=n_frame)
    ani.save('posterior_evolution.mp4', writer=writer)


def ground_truth():
    """Return a ground truth embedding."""
    kernel = psiz.models.ExponentialKernel()
    kernel.rho = 2.
    kernel.tau = 1.
    kernel.beta = 10.
    kernel.gamma = 0.001

    n_stimuli = 16
    n_dim = 2
    # Create a set of embedding points arranged in a grid pattern.
    x, y = np.meshgrid([.1, .2, .3, .4], [.1, .2, .3, .4])
    x = np.expand_dims(x.flatten(), axis=1)
    y = np.expand_dims(y.flatten(), axis=1)
    z = np.hstack((x, y))

    # Add a little noise to the embedding points to disrupt equal
    # distances.
    mean = np.zeros((n_dim))
    cov = .01 * np.identity(n_dim)
    z_noise = .1 * np.random.multivariate_normal(mean, cov, (n_stimuli))
    z = z + z_noise

    emb = psiz.models.Rank(
        n_stimuli, n_dim=n_dim, kernel=kernel
    )
    emb.z = z

    return emb


if __name__ == "__main__":
    main()
