# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.0.1]

### [Fixed]
 - An existing bug in constructing a JSON representation for a Pydantic model
   when the plate_number attribute is 2 or larger resulted in incorrect IDs
   being generated. The fix includes a return to using Pydantic models' built-in
   model_dump_json method in order to mitigate the risk that comes with  manual
   generation of JSON strings.

## [5.0.0]

### [Changed]

 - Stopped the mutation of the `plate_number` attribute at the time the
   PacBioEntity object instance is created. The value of the `plate_number`
   attribute is now stored and retrieved as supplied. As a consequence, the
   JSON string returned by the `model_dump_json` method of this Pydantic
   object is now different when `plate_namber` value is 1.
 - To retain backwards compatibility, the `hash_product_id` method is
   reimplemented since it can no longer use for ID generation the string
   returned by the `model_dump_json` method.

## [4.0.1]

### [Changed]

 - Upgrade python pydantic dependency to v2

## [4.0.0]

### Added

 - Add an extra PacBio entity attribute - plate_number.

## [3.0.0]

### Changed

 - Add validators for well label and tag patterns
 - Improve generator script help messages and change so that only named
   arguments are used
 - Make tag argument repeatable and add internal logic for concatenation

## [2.0.0]

### Fixed

 - Fixed a logical error in product id generation - the order or tags
   should not be changed by the generator.

## [1.0.1]

### Changed

 - Add tags argument to generate_pac_bio_id
 - Sort tags on creation of PacBioEntity object

## [1.0.0]

### Added

 - Ability to generate a product id for a PacBio well
