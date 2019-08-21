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
# or submit itself to any jurisdiction.

"""Disambiguation extension."""

from __future__ import absolute_import, division, print_function

import os

from . import config


class BeardConfig(object):
    config_data = None
    instance_path = os.path.dirname(os.path.abspath(__file__))

    def __new__(cls):
        if cls.config_data is not None:
            return cls.config_data
        else:
            cls.config_data = {}
            cls.init_config()
            return cls.config_data

    @classmethod
    def init_config(cls):
        disambiguation_base_path = os.path.join(cls.instance_path, 'disambiguation')

        cls.config_data['DISAMBIGUATION_BASE_PATH'] = disambiguation_base_path
        cls.config_data['DISAMBIGUATION_CURATED_SIGNATURES_PATH'] = os.path.join(
            disambiguation_base_path, 'curated_signatures.jsonl')
        cls.config_data['DISAMBIGUATION_INPUT_CLUSTERS_PATH'] = os.path.join(
            disambiguation_base_path, 'input_clusters.jsonl')
        cls.config_data['DISAMBIGUATION_SAMPLED_PAIRS_PATH'] = os.path.join(
            disambiguation_base_path, 'sampled_pairs.jsonl')
        cls.config_data['DISAMBIGUATION_PUBLICATIONS_PATH'] = os.path.join(
            disambiguation_base_path, 'publications.jsonl')
        cls.config_data['DISAMBIGUATION_ETHNICITY_DATA_PATH'] = os.path.join(
            disambiguation_base_path, 'ethnicity.csv')
        cls.config_data['DISAMBIGUATION_ETHNICITY_MODEL_PATH'] = os.path.join(
            disambiguation_base_path, 'ethnicity.pkl')
        cls.config_data['DISAMBIGUATION_DISTANCE_MODEL_PATH'] = os.path.join(
            disambiguation_base_path, 'distance.pkl')
        cls.config_data['DISAMBIGUATION_CLUSTERING_MODEL_PATH'] = os.path.join(
            disambiguation_base_path, 'clustering.pkl')
        cls.config_data['DISAMBIGUATION_CLUSTERING_N_JOBS'] = 8
        for k in dir(config):
            if k.isupper() and not k.startswith('__'):
                cls.config_data[k] = getattr(config, k)
