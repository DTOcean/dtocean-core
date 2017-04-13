# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

### Added

- Added tools plugin framework to add generic data manipulation or external
  tools.
- Increased the number of spectrum types available to the hydrodynamics wave
  submodule.
- Allowed filtering of the database when only sites or only devices are defined.
- Added tests for "System Type Selection" and "Site and System Options"
  interfaces.
- Add change log.

### Changed

- Renamed tools submodule to utils.
- Changed database stored proceedure calls to match changes to database
  structure.
- Added "category" and "group" fields to DDS and removed "symbol, sample_value,
  maximum_value, minimum_value, default_value, input_widget, output_widget"
  which were unused.
- Changed database table definitions to explicitly require the schema to be
  included, for instance project.farm rather than just farm.
- Changed table definitions in DDS files and configuration to work with
  new dtocean_examples database.
- Changed table references to filter.farm to filter.lease_area.
- Changed location of cable landing points to project.site table.
  
### Removed

- Schema is no longer set in database configuration.

### Fixed

- Fix missing type declarations in DDS for installation module outputs.
- Fixed PointData incorrectly storing coordinates passed as lists.
- Fix boolean inputs to installation module that require conversion to "yes/no".
- Fix incorrect device type in installation module test data. 

## [1.0.0] - 2017-02-23

### Added

- Initial import of dtocean-core from SETIS.
