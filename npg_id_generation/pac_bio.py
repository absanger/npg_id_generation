# Copyright (c) 2022, 2023, 2024 Genome Research Ltd.
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

import re
from hashlib import sha256
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def concatenate_tags(tags: list[str]):
    """Concatenates a list of tags so that it can be used as an attribute in
       the creation of a PacBioEntity.

    Args:
        tags: A list of tag sequences.

    Returns:A comma separated string of tags or None

    """
    if not tags:
        return None
    else:
        return ",".join(tags)


class PacBioEntity(BaseModel):
    """A PacBio class for product ID generation."""

    """
      Pydantic's current default is to serialize attributes in the order
      they are listed. if this behaviour changes, we can restore it by
      using json.dumps() sort_keys argument, see
      https://docs.python.org/3/library/json.html#basic-usage

      We are not using this explicit sort for now since it adds to the
      execution time.

      Order the attributes alphabetically to maintain order in the output
      of model_dump_json().
    """
    model_config = ConfigDict(extra="forbid")

    run_name: str = Field(title="Pac Bio run name as in LIMS")
    well_label: str = Field(title="Pac Bio well label")
    plate_number: Optional[int] = Field(
        default=None,
        ge=1,
        title="Pac Bio plate number",
        description="""
        Plate number is a positive integer and is relevant for Revio
        instruments only, thus it defaults to None.
        To be backward-compatible with Revio product IDs generated so far,
        when the value of this attribute is 1, it is ignored when serializing
        to generate an ID.
        """,
    )
    tags: Optional[str] = Field(
        default=None,
        title="A string representing tag or tags",
        description="""
        A string representing a single barcode index sequence (tag) or
        a comma-separated list of multiple tags. The order of tags in
        the list is meaningful for the purpose of product identification,
        therefore it should not be changed by the code of this class.
        """,
    )

    @field_validator("run_name", "well_label", "tags")
    def attributes_are_non_empty_strings(cls, v):
        if (v is not None) and (v == ""):
            raise ValueError("Cannot be an empty string")
        return v

    @field_validator("well_label")
    def well_label_conforms_to_pattern(cls, v):
        if not re.match("^[A-Z][1-9][0-9]?$", v):
            raise ValueError(
                "Well label must be an alphabetic character followed by a number between 1 and 99"
            )
        return v

    @field_validator("tags")
    def tags_have_correct_characters(cls, v):
        if (v is not None) and (not re.match("^[ACGT]+(,[ACGT]+)*$", v)):
            raise ValueError(
                "Tags should be a comma separated list of uppercase DNA sequences"
            )
        return v

    def hash_product_id(self):
        """Generate a sha256sum for the PacBio Entity"""

        if self.plate_number is not None and self.plate_number > 1:
            json = self.model_dump_json(exclude_none=True)
        else:
            json = self.model_dump_json(exclude_none=True, exclude=["plate_number"])

        return sha256(json.encode()).hexdigest()
