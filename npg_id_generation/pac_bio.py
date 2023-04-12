# Copyright (c) 2022, 2023 Genome Research Ltd.
#
# Authors:
#   Adam Blanchet <ab59@sanger.ac.uk>
#   Michael Kubiak <mk35@sanger.ac.uk>
#   Marina Gourtovaia <mg8@sanger.ac.uk>
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

from hashlib import sha256

from pydantic import BaseModel, Extra, Field, validator
import re


class PacBioEntity(BaseModel, extra=Extra.forbid):
    """A PacBio class for product ID generation."""

    # Order the attributes alphabetically, to allow for interoperability
    # with a possible Perl API.
    # Alternatively the sorting could be achieved with json.dumps()'s
    # sort_keys argument. See https://docs.python.org/3/library/json.html#basic-usage
    run_name: str = Field(title="Pac Bio run name as in LIMS")
    well_label: str = Field(title="Pac Bio well label")
    tags: str = Field(
        default=None,
        title="A string representing tag or tags",
        description="""
        A string representing a single barcode index sequence (tag) or
        a comma-separated list of multiple tags. The order of tags in
        the list is meaningful for the purpose of product identification,
        therefore it should not be changed by the code of this class.
        """,
    )

    @validator("run_name", "well_label", "tags")
    def attributes_are_non_empty_strings(cls, v):
        if (v is not None) and (v == ""):
            raise ValueError("Cannot be an empty string")
        return v

    @validator("well_label")
    def well_label_conforms_to_pattern(cls, v):
        if not re.match("^[A-Z][0-9]$", v):
            raise ValueError(
                "Well label must be an alphabetic character followed by a numeric character"
            )
        return v

    @validator("tags")
    def tags_have_correct_characters(cls, v):
        if (v is not None) and (not re.match("^[ACGT,]*$", v)):
            raise ValueError("Tags should be a comma separated list of DNA sequences")
        return v

    def hash_product_id(self):
        """Generate a sha256sum for the PacBio Entity"""

        return sha256(
            self.json(exclude_none=True, separators=(",", ":")).encode()
        ).hexdigest()
