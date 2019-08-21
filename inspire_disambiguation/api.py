# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction

"""Disambiguation API."""

from __future__ import absolute_import, division, print_function

from collections import defaultdict

import six

from inspire_disambiguation import conf
from .core.es.readers import (
    get_signatures,
)
from .core.ml.models import (
    Clusterer,
    DistanceEstimator,
    EthnicityEstimator,
)
from .core.ml.sampling import sample_signature_pairs_in_memory


def train_and_save_ethnicity_model():
    """Train the ethnicity estimator model and save it to disk."""
    estimator = EthnicityEstimator()
    estimator.load_data(conf['DISAMBIGUATION_ETHNICITY_DATA_PATH'])
    estimator.fit()
    estimator.save_model(conf['DISAMBIGUATION_ETHNICITY_MODEL_PATH'])


def train_and_save_distance_model(curated_signatures, pairs, sampled_pairs_size=None):
    """Train the distance estimator model and save it to disk."""
    if not sampled_pairs_size:
        sampled_pairs_size = conf['DISAMBIGUATION_SAMPLED_PAIRS_SIZE']
    ethnicity_estimator = EthnicityEstimator()
    ethnicity_estimator.load_model(conf['DISAMBIGUATION_ETHNICITY_MODEL_PATH'])

    distance_estimator = DistanceEstimator(ethnicity_estimator)
    distance_estimator.load_data(
        curated_signatures,
        pairs,
        sampled_pairs_size
    )
    distance_estimator.fit()
    distance_estimator.save_model(conf['DISAMBIGUATION_DISTANCE_MODEL_PATH'])


def train_clustering_model(signatures, input_clusters):
    """Train the clustering model and save it to disk."""
    ethnicity_estimator = EthnicityEstimator()
    ethnicity_estimator.load_model(conf['DISAMBIGUATION_ETHNICITY_MODEL_PATH'])

    distance_estimator = DistanceEstimator(ethnicity_estimator)
    distance_estimator.load_model(conf['DISAMBIGUATION_DISTANCE_MODEL_PATH'])

    clusterer = Clusterer(distance_estimator)
    clusterer.load_data(
        signatures,
        input_clusters,
    )
    clusterer.fit(n_jobs=conf['DISAMBIGUATION_CLUSTERING_N_JOBS'])
    return clusterer

