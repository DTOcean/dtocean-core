
import pytest
from collections import OrderedDict

import matplotlib.pyplot as plt

from dtocean_core.data import CoreMetaData
from dtocean_core.extensions import StrategyManager


@pytest.fixture(scope="module")
def manager():
    
    return StrategyManager()
    
    
def test_get_available(manager):
    
    result = manager.get_available()
    
    assert len(result) > 0
    
    
def test_get_strategy(manager):
    
    strategies = manager.get_available()
    
    for strategy_name in strategies:
        manager.get_strategy(strategy_name)
        
    assert True


def test_get_level_values_plot(mocker, manager):
    
    level_values = OrderedDict([
        ('Default', 
                     OrderedDict([('hydrodynamics global output',
                                   20000000.0),
                                  ('electrical sub-systems global output',
                                   23065408.054377057),
                                  ('mooring and foundations global output',
                                   28263096.852039404),
                                  ('installation global output',
                                   31673780.41058045),
                                  ('operations and maintenance global output',
                                   31673780.41058045)])),
        ('Default Clone 1',
                     OrderedDict([('hydrodynamics global output',
                                   20000000.0),
                                  ('electrical sub-systems global output',
                                   23065408.054377057),
                                  ('mooring and foundations global output',
                                   119195335.02247664),
                                  ('installation global output',
                                   123875364.39132734),
                                  ('operations and maintenance global output',
                                   123875364.39132734)]))])

    completed_levels = ['Hydrodynamics',
                        'Electrical Sub-Systems',
                        'Mooring and Foundations',
                        'Installation',
                        'Operations and Maintenance']
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    mocker.patch.object(manager,
                        'get_level_values',
                        return_value=level_values,
                        autospec=True)
    
    mocker.patch.object(manager._module_menu,
                        'get_completed',
                        return_value=completed_levels,
                        autospec=True)
    
    core = mocker.Mock()
    core.get_metadata.return_value = meta
    
    manager.get_level_values_plot(core,
                                  None,
                                  None)
    
    assert len(plt.get_fignums()) == 1
    
    ax = plt.gca()
    _, labels = ax.get_legend_handles_labels()
    
    assert len(labels) == 2
    
    plt.close("all")


def test_get_level_values_plot_max_lines(mocker, manager):
    
    level_values = OrderedDict([
        ('Default', 
                     OrderedDict([('hydrodynamics global output',
                                   20000000.0),
                                  ('electrical sub-systems global output',
                                   23065408.054377057),
                                  ('mooring and foundations global output',
                                   28263096.852039404),
                                  ('installation global output',
                                   31673780.41058045),
                                  ('operations and maintenance global output',
                                   31673780.41058045)])),
        ('Default Clone 1',
                     OrderedDict([('hydrodynamics global output',
                                   20000000.0),
                                  ('electrical sub-systems global output',
                                   23065408.054377057),
                                  ('mooring and foundations global output',
                                   119195335.02247664),
                                  ('installation global output',
                                   123875364.39132734),
                                  ('operations and maintenance global output',
                                   123875364.39132734)]))])

    completed_levels = ['Hydrodynamics',
                        'Electrical Sub-Systems',
                        'Mooring and Foundations',
                        'Installation',
                        'Operations and Maintenance']
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    mocker.patch.object(manager,
                        'get_level_values',
                        return_value=level_values,
                        autospec=True)
    
    mocker.patch.object(manager._module_menu,
                        'get_completed',
                        return_value=completed_levels,
                        autospec=True)
    
    core = mocker.Mock()
    core.get_metadata.return_value = meta
    
    manager.get_level_values_plot(core,
                                  None,
                                  None,
                                  max_lines=1)
    
    assert len(plt.get_fignums()) == 1
    
    ax = plt.gca()
    _, labels = ax.get_legend_handles_labels()
    
    assert len(labels) == 1
    
    plt.close("all")
