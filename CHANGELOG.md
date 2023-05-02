# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
