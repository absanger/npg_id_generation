# npg_id_generation

For different sequencing platforms different sets of attributes are used to
fully describe the origin of data. For reasons of efficiency and interoperability
between systems (for example, databases, long term data storage) it is
sometimes desirable to use a single identifier, which is globally unique.

Historically, the first algorithm for generating this kind of unique data
identifiers was implemented for the Illumina sequencing platform, see
[documentation](https://github.com/wtsi-npg/npg_tracking/blob/master/lib/npg_tracking/glossary/composition.pm).
In the Sanger Institute run ID, lane number and numerical tag index are used
to describe the origin of the data. The above Perl API uses these attributes of
the data to produce the unique ID.

Later a need to have a similar API for other sequencing platforms arose. This
package implements a Python API. The rationale for ID generation for an
arbitrary sequencing platform is as follows:

1. Implement a Python class that encapsulates a data model for the sequencing
   platform under consideration.
2. This class should have a constructor, which returns an object representing
   an instantiation of the data model for a particular set of attributes. The
   nature of these attributes might differ between sequencing platform.
3. This class should have an instance method that returns a unique ID.
4. This class should have an instance method that returns a human-readable
   JSON representation of the attributes that were given to the constructor.

All ID generators should conform to a few simple rules:

1. Uniqueness of the ID should be guaranteed.
2. The ID should be a 64 character string containing only hexadecimal digits.
3. The value of the ID should **not** depend on the order of attributes given
   to the constructor of the object that is used to generate the ID.
4. If the object, which is used to generate the ID, is instantiated from a JSON
   string, the value of the ID should **not** depend on the order of keys or
   the amount of whitespace in the input JSON.
5. The value of the ID should **not** depend on whether the undefined values
   of attributes are explicitly set.

The ID generator for the PacBio sequencing platform is implemented by the
`PacBioEntity` class.

Examples of generating IDs for PacBio data from Python code:

```python
from npg_id_generation.pac_bio import PacBioEntity

# from a JSON string via a class method
test_case = '{"run_name": "MARATHON","well_label": "D1"}'
print(PacBioEntity.parse_raw(test_case, content_type="json").hash_product_id())

# by setting object's attributes
print(PacBioEntity(run_name="MARATHON", well_label="D1").hash_product_id())
print(PacBioEntity(
    run_name="MARATHON",
    well_label="D1",
    plate_number=2
  ).hash_product_id()
)

# sample-specific indentifier
print(PacBioEntity(run_name="MARATHON", well_label="D1", tags="AAGTACGT").hash_product_id()
```

The npg_id_generation package also contains a script, `generate_pac_bio_id`,
which can be called from the command line. The script outputs the generated
ID to the STDOUT stream. Use the `--help` option to find out details.

```perl
# Using the script in the Perl code:
my $id = `generate_pac_bio_id --run_name 'MARATHON' --well_label 'D1'`;
```

The examples below clarify the rule any ID generator shoudl conform to.
Objects `o1` - `o6` should generate the same ID.

```python
o1 = PacBioEntity(run_name="r1", well_label="l1")
o2 = PacBioEntity(run_name="r1", well_label="l1", tags = None)
o3 = PacBioEntity(well_label="l1", run_name="r1", )
o4 = PacBioEntity.parse_raw('{"run_name": "r1","well_label": "l1"}', content_type="json")
o5 = PacBioEntity.parse_raw('{"well_label": "l1",  "run_name": "r1"}', content_type="json")
o6 = PacBioEntity.parse_raw('{"well_label": "l1","run_name": "r1", "tags": null}', content_type="json")
```
