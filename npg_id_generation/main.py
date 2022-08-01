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

from hashlib import sha256
from pydantic import BaseModel, Field


class PacBioEntity(BaseModel):
    """A PacBio entity class used to create hashes."""

    # Order these alphabetically, to allow for interoperability with
    # a possible Perl API.
    # Alternatively the sorting could be achieved with json.dumps()'s
    # sort_keys argument. See https://docs.python.org/3/library/json.html#basic-usage
    run_name: str
    well_label: str
    tags: str = Field(default=None)

    def hash_product_id(self):
        """Generate a sha256sum for the PacBioWell"""

        return sha256(
            self.json(exclude_none=True, separators=(",", ":")).encode()
        ).hexdigest()
