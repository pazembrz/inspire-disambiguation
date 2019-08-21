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


def get_signatures_and_input_clusters(curated=False, signature_block=None):
    signatures_with_author = defaultdict(list)
    all_signatures = []
    input_cluster = []
    curated_signatures=[]
    signatures_without_author = []

    if curated:
        signatures = get_signatures(curated=curated, signature_block=signature_block)
    else:
        signatures = get_signatures(signature_block=signature_block)
    for signature in signatures:
        if signature.get('author_id'):
            signatures_with_author[signature['author_id']].append(signature['signature_uuid'])
            curated_signatures.append(signature)
        else:
            signatures_without_author.append(signature['signature_uuid'])
        if not curated:
            all_signatures.append(signature)

    for cluster_id, (author_id, signature_uuids) in enumerate(six.iteritems(signatures_with_author)):
        input_cluster.append({
            'author_id': author_id,
            'cluster_id': cluster_id,
            'signature_uuids': signature_uuids,
        })

    for cluster_id, signature_uuid in enumerate(signatures_without_author, cluster_id + 1):
        input_cluster.append({
            'author_id': None,
            'cluster_id': cluster_id,
            'signature_uuids': [signature_uuid],
        })

    return {
        'signatures': all_signatures,
        'input_cluster': input_cluster,
        'curated_signatures': curated_signatures,
    }


def get_curated_signatures():
     = get_signatures(curated=True)



def train_and_save_ethnicity_model():
    """Train the ethnicity estimator model and save it to disk."""
    estimator = EthnicityEstimator()
    estimator.load_data(conf['DISAMBIGUATION_ETHNICITY_DATA_PATH'])
    estimator.fit()
    estimator.save_model(conf['DISAMBIGUATION_ETHNICITY_MODEL_PATH'])


def train_and_save_distance_model(curated_signatures, clusters, publications):
    """Train the distance estimator model and save it to disk."""
    pairs = sample_signature_pairs_in_memory(
        curated_signatures,
        clusters,
        conf['DISAMBIGUATION_SAMPLED_PAIRS_SIZE']
    )
    ethnicity_estimator = EthnicityEstimator()
    ethnicity_estimator.load_model(conf['DISAMBIGUATION_ETHNICITY_MODEL_PATH'])

    distance_estimator = DistanceEstimator(ethnicity_estimator)
    distance_estimator.load_data(
        curated_signatures,
        pairs,
        conf['DISAMBIGUATION_SAMPLED_PAIRS_SIZE'],
        publications
    )
    distance_estimator.fit()
    distance_estimator.save_model(conf['DISAMBIGUATION_DISTANCE_MODEL_PATH'])


def train_clustering_model(signatures, publications, input_clusters):
    """Train the clustering model and save it to disk."""
    ethnicity_estimator = EthnicityEstimator()
    ethnicity_estimator.load_model(conf['DISAMBIGUATION_ETHNICITY_MODEL_PATH'])

    distance_estimator = DistanceEstimator(ethnicity_estimator)
    distance_estimator.load_model(conf['DISAMBIGUATION_DISTANCE_MODEL_PATH'])

    clusterer = Clusterer(distance_estimator)
    clusterer.load_data(
        signatures,
        publications,
        input_clusters,
    )
    clusterer.fit(n_jobs=conf['DISAMBIGUATION_CLUSTERING_N_JOBS'])
    return clusterer

