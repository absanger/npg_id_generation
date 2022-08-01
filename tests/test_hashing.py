# Copyright (c) 2022 Genome Research Ltd.
#
# Author: Adam Blanchet <ab59@sanger.ac.uk>
#
# This file is part of npg_id_generation.
#
# npg_langqc is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

"""Tests checking the hashing behaviour of input objects."""

from npg_id_generation.main import PacBioEntity


def test_different_orderings():
    """The output hash should not depend on the order of keys."""

    test_cases = [
        '{"run_name": "MARATHON","well_label": "D1"}',
        '{"well_label": "D1", "run_name": "MARATHON"}',
    ]

    results = [
        PacBioEntity.parse_raw(test_case, content_type="json").hash_product_id()
        for test_case in test_cases
    ]

    assert len(set(results)) == 1


def test_whitespace():
    """The output hash should not depend on whitespace in the input JSON."""

    test_cases = [
        '{"run_name":"MARATHON","well_label":"D1"}',
        '{     "run_name":     "MARATHON",    "well_label":     "D1"}',
        '   {"run_name":  "MARATHON","well_label": "D1"   }',
        '\n\n\n\n\t{"run_name"\t:\n  \t  \n"MARATHON",\n"well_label": \n\n  "D1"      } ',
    ]

    results = [
        PacBioEntity.parse_raw(test_case, content_type="json").hash_product_id()
        for test_case in test_cases
    ]

    assert len(set(results)) == 1
