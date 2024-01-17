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
        PacBioEntity.model_validate_json(test_case).hash_product_id()
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
        PacBioEntity.model_validate_json(test_case).hash_product_id()
        for test_case in test_cases
    ]

    assert len(set(results)) == 1


def test_different_ways_to_create_object():
    results = [
        PacBioEntity(run_name="MARATHON", well_label="A1").hash_product_id(),
        PacBioEntity(well_label="A1", run_name="MARATHON").hash_product_id(),
        PacBioEntity(run_name="MARATHON", well_label="A1", tags=None).hash_product_id(),
        PacBioEntity.model_validate_json(
            '{"run_name": "MARATHON", "well_label": "A1"}'
        ).hash_product_id(),
    ]
    assert len(set(results)) == 1

    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity(run_name="MARATHON", well_label="A1", some_arg=3)
    assert "Extra inputs are not permitted" in str(excinfo.value)


def test_tags_make_difference():
    id_1 = PacBioEntity(
        run_name="MARATHON", well_label="A1", tags="ACGT"
    ).hash_product_id()
    id_2 = PacBioEntity(
        run_name="MARATHON", well_label="A1", tags="ACTG"
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
        PacBioEntity.model_validate_json('{"run_name": "MARATHON", "well_label": ""}')
    assert "Cannot be an empty string" in str(excinfo.value)


def test_well_label_conforms_to_pattern():
    bad_labels = [" A1", "A1 ", "A01", "1A"]
    for label in bad_labels:
        with pytest.raises(ValidationError) as excinfo:
            PacBioEntity(run_name="MARATHON", well_label=label)
        assert (
            "Well label must be an alphabetic character followed by a number between 1 and 99"
            in str(excinfo.value)
        )
    with pytest.raises(ValidationError) as excinfo:
        PacBioEntity.model_validate_json('{"run_name": "MARATHON", "well_label":"1A"}')
    assert (
        "Well label must be an alphabetic character followed by a number between 1 and 99"
        in str(excinfo.value)
    )


def test_tags_have_correct_characters():
    bad_tags = [
        "ABCD",
        "ACGT.AGTC",
        " ACGT",
        "ACGT ",
        "acgt",
        ",",
        " ACCTG ",
        "ACCTG,",
        ",ACCTG",
        "ACCTG,,GGTAC",
    ]
    for tag in bad_tags:
        with pytest.raises(ValidationError) as excinfo:
            PacBioEntity(run_name="MARATHON", well_label="A1", tags=tag)
        assert (
            "Tags should be a comma separated list of uppercase DNA sequences"
            in str(excinfo.value)
        )


def test_plate_number_validation():
    for n in [-1, 0]:
        with pytest.raises(ValidationError) as excinfo:
            PacBioEntity(run_name="MARATHON", well_label="A1", plate_number=n)
        assert "Input should be greater than or equal to 1" in str(excinfo.value)


def test_plate_number_defaults():
    """Test backwards compatibility for the plate number"""

    e1 = PacBioEntity(run_name="MARATHON", well_label="A1", tags="TAGC", plate_number=1)
    e2 = PacBioEntity(run_name="MARATHON", well_label="A1", tags="TAGC")
    e3 = PacBioEntity(
        run_name="MARATHON", well_label="A1", tags="TAGC", plate_number=None
    )
    assert e1.plate_number is 1
    assert e2.plate_number is None
    assert e3.plate_number is None
    assert e1.model_dump_json(exclude_none=True) != e2.model_dump_json(
        exclude_none=True
    )
    assert e1.model_dump_json(exclude_none=True) != e3.model_dump_json(
        exclude_none=True
    )
    assert e1.hash_product_id() == e2.hash_product_id()
    assert e1.hash_product_id() == e3.hash_product_id()

    e1 = PacBioEntity(run_name="MARATHON", well_label="A1", plate_number=1)
    e2 = PacBioEntity(run_name="MARATHON", well_label="A1")
    assert e1.plate_number is 1
    assert e2.plate_number is None
    assert e1.model_dump_json() != e2.model_dump_json()
    assert e1.hash_product_id() == e2.hash_product_id()


def test_multiple_plates_make_difference():
    id_1 = PacBioEntity(
        run_name="MARATHON", well_label="A1", tags="ACGT"
    ).hash_product_id()
    id_2 = PacBioEntity(
        run_name="MARATHON", well_label="A1", tags="ACGT", plate_number=2
    ).hash_product_id()
    id_3 = PacBioEntity(
        run_name="MARATHON", well_label="A1", tags="ACGT", plate_number=3
    ).hash_product_id()
    assert id_1 != id_2
    assert id_3 != id_2

    id_1 = PacBioEntity(run_name="MARATHON", well_label="A1").hash_product_id()
    id_2 = PacBioEntity(
        run_name="MARATHON", well_label="A1", plate_number=2
    ).hash_product_id()
    id_3 = PacBioEntity(
        run_name="MARATHON", well_label="A1", plate_number=3
    ).hash_product_id()
    assert id_1 != id_2
    assert id_3 != id_2

    json = PacBioEntity(
        run_name="MARATHON", well_label="A1", plate_number=2
    ).model_dump_json(exclude_none=True)
    assert json == '{"run_name":"MARATHON","well_label":"A1","plate_number":2}'
    json = PacBioEntity(
        run_name="MARATHON", well_label="A1", tags="ACTGG", plate_number=2
    ).model_dump_json(exclude_none=True)
    assert (
        json
        == '{"run_name":"MARATHON","well_label":"A1","plate_number":2,"tags":"ACTGG"}'
    )


def test_expected_hashes():
    """Test against expected hashes."""
    # plate_number absent (historical runs) or plate_number == 1
    p1_sha256 = "cda15311f706217e31e32d42d524bc35662a6fc15623ce5abe6a31ed741801ae"
    # plate_number == 2
    p2_sha256 = "7ca9d350c9b14f0883ac568220b8e5d97148a4eeb41d9de00b5733299d7bcd89"

    test_cases = [
        ('{"run_name": "MARATHON", "well_label": "A1"}', p1_sha256),
        ('{"run_name": "MARATHON", "well_label": "A1", "plate_number": 1}', p1_sha256),
        ('{"run_name": "MARATHON", "well_label": "A1", "plate_number": 2}', p2_sha256),
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
            PacBioEntity.model_validate_json(json_str).hash_product_id()
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


def test_regression_github_issue19():
    # https://github.com/wtsi-npg/npg_id_generation/issues/19

    e1 = PacBioEntity(run_name="MARATHON", well_label="A1", tags="ACGT", plate_number=1)
    assert e1.plate_number == 1, "Plate number should be 1 and not None"
