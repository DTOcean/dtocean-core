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
- Added more complete device subsystem descriptions for maintenance module.
  These split the requirements for each subsystem for access and the different
  maintenance strategies.
- Added DateTimeDict data structure for dictionaries of datetime.datetime
  objects.
- Completed database integration for installation and maintenance modules.
- Add change log.
- Added better error if predefined array layout option is chosen but no layout
  is given.
- Added more comprehensive tests of various Structure subclasses.
- Allow suppression of datastate output level when executing interfaces using
  Connector.execute_interface. All DB output interfaces are no longer tagged
  with an output level and are not hidden when using module-only output scope.
- Added plots for tidal stream velocities over the domain, choosing a random
  time point.
- Added configuration file for setting the location of logs and debug files
  using the files.ini configuration file (found in
  User\AppData\Roaming\DTOcean\dtocean_core\config folder).
- Added configuration file generator called dtocean-core-config which copies
  the default configuration to the
  User\AppData\Roaming\DTOcean\dtocean_core\config folder.
- Added labels and units to various variables using PointDict structure.
- Added key annotation to PointDict plots.
- Added "Lease Area Array Layout" plot to show devices in relation to the lease
  area definition.
- Added "Te & Hm0 Time Series" to show the Te and Hm0 time series separately
  from the wave directions.
- Added "Wave Resource Occurrence Matrix" plot to show the wave module
  occurrence matrix over all wave directions.
- Added logging of module execution time (requires monotonic package).
- Added robustness to opening dto files from older versions of the software.
  Note, datastate corruption may still occur and new data may need to be added.
- Added capacity factor as an output of the hydrodynamics interface.
- Added plots for electrical cable layout.
- Added plot for foundations layout.
- Added optional boundary padding input to the electrical module so that the
  substation can be moved away from the lease area edge.
- Added operational limit conditions to data catalogue to allow modification
  in the installation interface.
- Added "passive hub" as a valid collection point type in the installation
  interface.

### Changed

- Renamed tools submodule to utils.
- Changed database stored procedure calls to match changes to database
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
- Improved plot labelling and included Latex symbols.
- Reordered Hydrodynamics module inputs.
- Renamed test_structures as test_definitions.
- SQLAlchemy calls moved out of structure definitions and into utils.database.
  This allows for easier testing of structure database read code.
- Reorganised plot interfaces to have separate files for related data.
- Changed setup.py to copy configuration files from source code to AppData as a
  post-install step.
- Using default configuration files in source code unless a user configuration
  is found, or if the database definitions are written using
  DataMenu.update_database.
- SimpleDict bar plots are now sorted by label.
- Changed title of project.array_efficiency variable metadata to Array Capacity
  Factor.
- Reordered electrical module inputs and outputs.
- Switched timed rotating file logger for a standard rotating file logger which
  is rolled over at each invocation of start_logging.
- Modified order of moorings and foundations module inputs.

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
- Fixed bugs with database reading empty tables - now returns None.
- Fixed TimeSeries structure plots.
- Fixed soil type name conversions with the Electrical module interface.
- Fixed bug in PointList structure file I/O.
- Fixed power histogram calculation which was not ordering the powers
  correctly.
- Fixed file I/O and plots for NumpyLineDict and HistogramDict structures.
- Fix issue with None values in the sediments layers being incorrectly passed
  to the moorings module.
- Fix issues with formatting of some tabulated outputs of the moorings module.
- Fixed missing variable mapping in constraints plot tool interface. It uses
  the input declaration of the electrical module interface, but its own id_map
  and so they went out of sync following changes to the electrical interface.

### Removed

- Schema is no longer set in database configuration.
- Removed farm.point_sea_surface_height
- Removed lead times as unused.
- Remove unused power quality variables.
- Removed unused switchgear variables.
- Removed numerous unused fields from component tables.
- Removed numerous unused fields from equipment tables.
- Removed numerous unused fields from ports table.
- Removed numerous unused fields from vessels table.
- Removed some header lines from inputs to moorings module and hard coded them
  into the interface.
- Removed power law exponent variable as this is not used when Manning's number
  is used to describe channel roughness.
- Removed variables that are inputs to the electrical module but are not used 
  in any way.
- Remove adjust_outliers options from make_power_histograms as was always set
  to True.

## [1.0.0] - 2017-02-23

### Added

- Initial import of dtocean-core from SETIS.
