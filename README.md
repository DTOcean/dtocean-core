[![appveyor](https://ci.appveyor.com/api/projects/status/github/DTOcean/dtocean-core?branch=master&svg=true)](https://ci.appveyor.com/project/DTOcean/dtocean-core)
[![codecov](https://codecov.io/gh/DTOcean/dtocean-core/branch/master/graph/badge.svg)](https://codecov.io/gh/DTOcean/dtocean-core)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/bb34506cc82f4df883178a6e64619eaf)](https://www.codacy.com/project/H0R5E/dtocean-core/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=DTOcean/dtocean-core&amp;utm_campaign=Badge_Grade_Dashboard&amp;branchId=8410911)
[![release](https://img.shields.io/github/release/DTOcean/dtocean-core.svg)](https://github.com/DTOcean/dtocean-core/releases/latest)

# DTOcean Core Module

The dtocean-core module provides the model for the DTOcean suite of tools. It
manages data transfer and between the DTOcean components (modules, database,
user), data storage and versioning, and module execution ordering.

## Installation

Installation and development of aneris uses the [Anaconda Distribution](
https://www.anaconda.com/distribution/) (Python 2.7)

### DTOcean Modules

Since version 2.0.0, dtocean-core is not dependent on installation of
dtocean design or assessment modules. This means a user could choose to use
dtocean-core for working with just one module, if desired.

Installation instructions for each desired module should be followed, although 
it is recommended to start by installing this module, or [dtocean-app]
(https://github.com/DTOcean/dtocean-app), first if installing from source.

### Conda Package

To install:

```
$ conda install -c defaults -c conda-forge -c dataonlygreater dtocean-core
```

DTOcean modules for use with the core must be installed separately. For example:

```
$ conda install -c dataonlygreater dtocean-hydrodynamics
```

See the README.md file of each module for conda installation instructions.

### Source Code

Conda can be used to install dependencies into a dedicated environment from
the source code root directory:

```
$ conda create -n _dtocean_core python=2.7 pip
```

Activate the environment, then copy the `.condrc` file to store installation  
channels and pin critical packages to ensure stable installation of multiple 
DTOcean modules:

```
$ conda activate _dtocean_core
$ copy .condarc %CONDA_PREFIX%
```

Install [polite](https://github.com/DTOcean/polite) and [aneris](
https://github.com/DTOcean/aneris) into the environment. For example, if 
installing them from source:

```
$ cd \\path\\to\\polite
$ conda install --file requirements-conda-dev.txt
$ pip install -e .

$ cd \\path\\to\\aneris
$ conda install --file requirements-conda-dev.txt
$ pip install -e .
```

**Install any other required DTOcean packages at this point**. For instance,
to install all the design and assessment modules using conda packages:

```
$ conda install dtocean-hydrodynamics ^
                dtocean-electrical ^
                dtocean-moorings ^
                dtocean-installation ^
                dtocean-maintenance ^
                dtocean-economics ^
                dtocean-reliability ^
                dtocean-environment
```

Notes:

 * The above command will overwrite the source installed version of polite.
   To avoid this, install all required DTOcean packages from source, or
   uninstall the conda version of polite (`conda remove polite`) and reinstall 
   from source using pip.
 * If using dtocean-hydrodynamics, you must also install the hydrodynamic data 
   package. See the [dtocean-hydrodynamics](
   https://github.com/DTOcean/dtocean-hydrodynamics) repository for 
   installation instructions.
 * The core can read module inputs from the DTOcean database. See the 
  [dtocean-database](https://github.com/DTOcean/dtocean-database) repository 
  for installation instructions.

A "bootstrapping" stage is required to prepare the data catalogue files:

```
$ cd \\path\\to\\dtocean-core
% python setup.py bootstrap
``` 

Finally, install dtocean-core and its dependencies using conda and pip (don't
worry if some packages are downgraded during this process):

```
$ conda install --file requirements-conda-dev.txt
$ pip install -e .
```

To deactivate the conda environment:

```
$ conda deactivate
```

### Tests

A test suite is provided with the source code that uses [pytest](
https://docs.pytest.org).

If not already active, activate the conda environment set up in the [Source 
Code](#source-code) section:

```
$ conda activate _dtocean_core
```

Install pytest to the environment (one time only):

```
$ conda install -y pytest pytest-mock
```

Run the tests:

``` 
$ python setup.py test
```

### Uninstall

To uninstall the conda package:

```
$ conda remove dtocean-core
```

To uninstall the source code and its conda environment:

```
$ conda remove --name _dtocean_core --all
```

## Usage

### Jupyter Notebooks

Examples of using dtocean-core are given in [Jupyter Notebooks](
http://jupyter.org/) which are found in the "notebooks" folder of the
dtocean-core source code. The notebooks should be used from the installation
conda environment. To install jupyter:

```
$ activate _dtocean_core
$ conda install -y jupyter ipykernel=4.8.2
```

Then, to start the jupyter notebook in your default browser:

```
$ start jupyter notebook
```

Note, you only need to activate the environment once per session.

**It is important that the "test_data" directory is copied into the same
directory where the notebooks are being executed from**. You can customise this
directory using the config file described [here](
http://jupyter-notebook.readthedocs.io/en/latest/config.html) and setting the 
"notebook_dir" variable.

Once the test_data directory has been placed alongside the notebook, the 
notebook can be executed in the normal way.

### Command Line Tools

A utility is provided to add an energy period (Te) time series to wave data 
containing significant wave height (Hm0) and wave peak period (Tp). To get help:

```
$ add-Te -h
```

Another utility is provided to copy user modifiable configuration files to the
users "AppData" directory (on Windows). For instance the logging and database
configuration can be modified once these files have been copied. To get help:

```
$ dtocean-core-config -h
```

Finally, a utility for converting the DTOcean SQL database into a structured
directories of files, or for uploading the same structure into the database is
provided. To get help:

```
$ dtocean-database -h
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

See [this blog post](
https://www.dataonlygreater.com/latest/professional/2017/03/09/dtocean-development-change-management/)
for information regarding development of the DTOcean ecosystem.

Please make sure to update tests as appropriate.

## Credits

This package was initially created as part of the [EU DTOcean project](
https://www.dtoceanplus.eu/About-DTOceanPlus/History) by:

 * Mathew Topper at [TECNALIA](https://www.tecnalia.com)
 * Vincenzo Nava at [TECNALIA](https://www.tecnalia.com)
 * Adam Colin at [the University of Edinburgh](https://www.ed.ac.uk/)
 * David Bould at [the University of Edinburgh](https://www.ed.ac.uk/)
 * Rui Duarte at [France Energies Marines](https://www.france-energies-marines.org/)
 * Francesco Ferri at [Aalborg University](https://www.en.aau.dk/)

It is now maintained by Mathew Topper at [Data Only Greater](
https://www.dataonlygreater.com/).

## License

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)
