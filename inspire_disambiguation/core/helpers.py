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

"""Disambiguation helpers."""
from inspire_schemas.readers import LiteratureReader
from inspire_utils.helpers import maybe_int
from inspire_utils.record import get_value

from inspire_disambiguation.core.ml.models import Publication, Signature


def _get_author_affiliation(author):
    return get_value(author, 'affiliations.value[0]', default='')


def _get_author_id(author):
    if author.get('curated_relation'):
        return get_recid_from_ref(author.get('record'))


def _build_signature(author, record):
    return Signature(**{
        'author_affiliation': _get_author_affiliation(author),
        'author_id': _get_author_id(author),
        'author_name': author['full_name'],
        'publication': Publication(**_build_publication(record)),
        'signature_block': author.get('signature_block'),
        'signature_uuid': author['uuid'],
    })


def get_recid_from_ref(ref_obj):
    """Retrieve recid from jsonref reference object.
    If no recid can be parsed, returns None.
    """
    if not isinstance(ref_obj, dict):
        return None
    url = ref_obj.get('$ref', '')
    return maybe_int(url.split('/')[-1])


def _build_publication(record):
    reader = LiteratureReader(record)
    return {
        'abstract': reader.abstract,
        'authors': _get_authors(record),
        'collaborations': reader.collaborations,
        'keywords': reader.keywords,
        'publication_id': record['control_number'],
        'title': reader.title,
        'topics': reader.inspire_categories,
    }


def _get_authors(record):
    return get_value(record, 'authors.full_name', default=[])
