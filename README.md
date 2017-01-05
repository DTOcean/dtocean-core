# DTOcean Core Module (Version "release")

## Installation

### Install Hydrodynamics Data Package

The following hydrodynamic data package should be downloaded and installed:

* dtocean-hydrodynamic-data-1.0-standalone.exe

Once downloaded execute the file to install. Remember to uninstall any old
versions first using the uninstaller in the DTOcean Hydrodynamics start menu
program folder.

### Set up an Anaconda environment

Using a windows command prompt enter the following commands:

```
conda create -n _dtocean python pip pytest ipython-notebook
```

then, to activate the environment:

```
activate _dtocean
```

or

```
C:\Anaconda\Scripts\activate.bat dtocean_integration
```

### Add Public Anaconda Cloud channel

To download the alpha version of the core the following channel must be
added to Ananconda:

```
conda config --add channels https://conda.anaconda.org/topper
```

Note, this is operation should only be done once.

### Install Package Dependencies

```
conda install attrdict basemap cma configobj descartes dtocean-demo-package geoalchemy2 h5py libpython=1.0 matplotlib netcdf4 networkx numpy=1.10.1 openpyxl pandas pil psycopg2-win-py27 pyproj pyopengl pypower pyqt=4.11.4 pywin32 pyyaml scikit-learn scipy setuptools shapely-win-py27 sqlalchemy xarray xlrd xlwt
```

### Install "dev" Package Versions

Three packages must be installed separately either from the "dev"
branches of the Hg repositories found in https://bitbucket.org/team_dtocean.
The required packages (and branches) are:

* polite
* aneris
* dtocean-hydrodynamics
* dtocean-electrical
* dtocean-moorings-foundations
* dtocean-installation
* dtocean-operations-and-maintenance
* dtocean-economics
* dtocean-environmental
* dtocean-reliability
* dtocean-core

A good package for managing Hg repositories is [TortoiseHg](http://tortoisehg.bitbucket.org/).

The packages below should be cloned and updating to their "dev"
branch. Then, issue the following commands in a command window:

```
cd path\to\polite
winmake.bat install
```

```
cd path\to\aneris
winmake.bat install
```

```
cd path\to\dtocean-hydrodynamics
winmake.bat bootstrap
```

```
cd path\to\dtocean-electrical
winmake.bat install
```

```
cd path\to\dtocean-moorings-foundations
winmake.bat install
```

```
cd path\to\dtocean-installation
winmake.bat install
```

```
cd path\to\dtocean-operations-and-maintenance
winmake.bat install
```

```
cd path\to\dtocean-economics
winmake.bat install
```

```
cd path\to\dtocean-environmental
winmake.bat install
```

```
cd path\to\dtocean-reliability
winmake.bat install
```

```
cd path\to\dtocean-core
winmake.bat bootstrap
```

## Testing

### Unit Tests

Unit tests will run automatically as part of the package installation process. 
They can be re-run using the command:

```
cd path\to\package
winmake.bat test
```

### Jupyter Notebooks

Examples of using the Core are given in [Jupyter Notebooks](http://jupyter.org/)
which are found in the "Notebooks" folder of the dtocean-core source code. The
notebooks should be started from the Anaconda environment as follows:

```
activate _dtocean
start jupyter notebook
```

Note, you only need to activate the environment once per session.

**It is important that the test data found in the "test_data" directory is
copied into the same directory where the notebooks are being executed from**.
You can customise this directory using the config file described
[here](http://jupyter-notebook.readthedocs.io/en/latest/config.html)
and setting the "notebook_dir" variable.

Once the test data has been placed alongside the notebook, the notebook can be
executed in the normal way.

## DTOcean Project

DTOcean - "Optimal Design Tools for Ocean Energy Arrays" is funded by the 
European Commission’s 7th Framework Programme. Grant agreement number: 608597
