"""Tests checking the hashing behaviour of objects."""

import pytest
from pydantic import ValidationError

from npg_id_generation.pac_bio import PacBioEntity


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


def test_different_ways_to_create_object():
    results = []
    results.append(PacBioEntity(run_name="MARATHON", well_label="A1").hash_product_id())
    results.append(PacBioEntity(well_label="A1", run_name="MARATHON").hash_product_id())
    results.append(
        PacBioEntity(run_name="MARATHON", well_label="A1", tags=None).hash_product_id()
    )
    results.append(
        PacBioEntity.parse_raw(
            '{"run_name": "MARATHON", "well_label": "A1"}', content_type="json"
        ).hash_product_id()
    )
    assert len(set(results)) == 1

    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity(run_name="MARATHON", well_label="A1", some_arg=3)
    assert "extra fields not permitted" in str(excinfo.value)


def test_tags_make_difference():
    id_1 = PacBioEntity(
        run_name="MARATHON", well_label="A1", tags="acgt"
    ).hash_product_id()
    id_2 = PacBioEntity(
        run_name="MARATHON", well_label="A1", tags="actg"
    ).hash_product_id()
    id_3 = PacBioEntity(run_name="MARATHON", well_label="A1").hash_product_id()
    assert id_1 != id_2
    assert id_3 != id_2


def test_attributes_cannot_be_empty():
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity(run_name="MARATHON", well_label="A1", tags="")
    assert "Cannot be an empty string" in str(excinfo.value)
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity(run_name="", well_label="A1")
    assert "Cannot be an empty string" in str(excinfo.value)
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity(run_name="MARATHON", well_label="")
    assert "Cannot be an empty string" in str(excinfo.value)
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity.parse_raw(
            '{"run_name": "MARATHON", "well_label": ""}', content_type="json"
        )
    assert "Cannot be an empty string" in str(excinfo.value)


def test_well_label_conforms_to_pattern():
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity(run_name="MARATHON", well_label=" A1")
    assert (
        "Well label must be an alphabetic character followed by a numeric character"
        in str(excinfo.value)
    )
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity(run_name="MARATHON", well_label="A1 ")
    assert (
        "Well label must be an alphabetic character followed by a numeric character"
        in str(excinfo.value)
    )
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity(run_name="MARATHON", well_label="A01")
    assert (
        "Well label must be an alphabetic character followed by a numeric character"
        in str(excinfo.value)
    )
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity(run_name="MARATHON", well_label="1A")
    assert (
        "Well label must be an alphabetic character followed by a numeric character"
        in str(excinfo.value)
    )
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity.parse_raw(
            '{"run_name": "MARATHON", "well_label":"1A"}', content_type="json"
        )
    assert (
        "Well label must be an alphabetic character followed by a numeric character"
        in str(excinfo.value)
    )


def test_tags_have_correct_characters():
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity(run_name="MARATHON", well_label="A1", tags="ABCD")
    assert "Tags should be a comma separated list of DNA sequences" in str(
        excinfo.value
    )
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity(run_name="MARATHON", well_label="A1", tags="ACGT.AGTC")
    assert "Tags should be a comma separated list of DNA sequences" in str(
        excinfo.value
    )
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity(run_name="MARATHON", well_label="A1", tags=" ACGT")
    assert "Tags should be a comma separated list of DNA sequences" in str(
        excinfo.value
    )
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity(run_name="MARATHON", well_label="A1", tags="ACGT ")
    assert "Tags should be a comma separated list of DNA sequences" in str(
        excinfo.value
    )
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity.parse_raw(
            '{"run_name":"MARATHON", "well_label":"A1", "tags":"ABCD"}'
        )
    assert "Tags should be a comma separated list of DNA sequences" in str(
        excinfo.value
    )


def test_expected_hashes():
    """Test against expected hashes."""

    test_cases = [
        (
            '{"run_name": "MARATHON", "well_label": "A1"}',
            "cda15311f706217e31e32d42d524bc35662a6fc15623ce5abe6a31ed741801ae",
        ),
        (
            '{"run_name": "SEMI-MARATHON", "well_label": "D1"}',
            "b55417615e458c23049cc84822531a435c0c4069142f0e1d5e4378d48d9f7bd2",
        ),
        (
            '{"run_name": "MARATHON", "well_label": "D1"}',
            "1043340167120b5b75b4c76a364b72f960e429f0103a03208f257d3ed8994196",
        ),
        (
            '{"run_name": "SEMI-MARATHON", "well_label": "B1"}',
            "e2a676471c83dafafd1f93628e492c064dbf762a6983e7baa723d60f015d05fc",
        ),
    ]

    for json_str, expected_hash in test_cases:
        assert (
            PacBioEntity.parse_raw(json_str, content_type="json").hash_product_id()
            == expected_hash
        )


def test_tags_not_sorted():
    """Test that tags are not changed prior to id generation"""

    run = "MARATHON"
    well = "A1"
    # Tags in these strings are the same, the difference is
    # in the order.
    tags_strings = ["TCGA,ACGT,TGAC,AACG", "ACGT,AACG,TGAC,TCGA", "TGAC,TCGA,AACG,ACGT"]
    pb_entities = []
    for tag_string in tags_strings:
        pb_entities.append(PacBioEntity(run_name=run, well_label=well, tags=tag_string))

    assert (
        pb_entities[0].hash_product_id()
        != pb_entities[1].hash_product_id()
        != pb_entities[2].hash_product_id()
    )
