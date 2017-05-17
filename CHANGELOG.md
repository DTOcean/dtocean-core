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
- Added new parameter for recording JONSWAP spectrum gamma value in extreme
  calculations used by the moorings module.
- Added more complete device subsystem descriptions for maintanence module.
  These split the requirements for each subsystem for access and the different
  maintanence strategies.
- Added DateTimeDict data structure for dictionaries of datetime.datetime
  objects.
- Completed database integration for installation and maintanence modules.
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
- Changed categories (i.e category.name) of multiple variables to make a 
  clear distinction between site, device, reference and project specific data.
- Device construction strategy is now simplified to offer just a "two stage
  assembly" option.
- Split vessels table into separate tables per vehicle type.

### Fixed

- Fix missing type declarations in DDS for installation module outputs.
- Fixed PointData incorrectly storing coordinates passed as lists.
- Fix boolean inputs to installation module that require conversion to
  "yes/no".
- Fix incorrect device type in installation module test data. 
- Fixed units of directions to electrical module which required conversion to
  radians.
- Fixed spectrum definitions to hydrodynamics module.
- Fix use of fibre optic channels variable in electrical module interfaces
- Fix use of device bollard pull in installation module interface.
- Merged umbilical table and dynamic cable tables.
- Fixed installation module dates based outputs.
- General improvements to variable and table column names.
- Fixed chosen trenching type variable definition.
   
### Removed

- Schema is no longer set in database configuration.
- Removed farm.point_sea_surface_height
- Removed lead times as unused.
- Remove unused power qulaity variables.
- Removed unused switchgear variables.
- Removed numerous unused fields from component tables.
- Removed numerous unused fields from equipment tables.
- Removed numerous usused fields from ports table.
- Removed numerous usused fields from vessels table.
- Removed some header lines from inputs to moorings module and hard coded them
  into the interface. 

## [1.0.0] - 2017-02-23

### Added

- Initial import of dtocean-core from SETIS.
