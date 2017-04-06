# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

### Added

- Added tools plugin framework to add generic data manipulation or external
  tools.
- Add change log.

### Changed

- Renamed tools submodule to utils.
- Changed database stored proceedure calls to match changes to database
  structure.

### Fixed

- Fix missing type declarations in DDS for installation module outputs.
- Fixed PointData incorrectly storing coordinates passed as lists.
- Fix boolean inputs to installation module that require conversion to "yes/no".
- Fix incorrect device type in installation module test data. 

## [1.0.0] - 2017-02-23

### Added

- Initial import of dtocean-core from SETIS.