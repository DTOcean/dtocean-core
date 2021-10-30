# -*- coding: utf-8 -*-

import pytest

from dtocean_core.strategies.position import AdvancedPosition


@pytest.fixture()
def advanced():
    return AdvancedPosition()


def test_advanced_get_name():
    assert AdvancedPosition.get_name() == "Advanced Positioning"


def test_advanced_get_config_fname():
    assert AdvancedPosition.get_config_fname() == "config.yaml"


@pytest.mark.parametrize("param,            exp_status_str, exp_status_code", [
                         (None,             "incomplete",   0),
                         ("results_params", "complete",     1)])
def test_advanced_get_config_status(param, exp_status_str, exp_status_code):
    
    keys = ["root_project_path",
            "worker_dir",
            "base_penalty",
            "n_threads",
            "parameters",
            "objective"]
    
    if param is not None: keys.append(param)
    
    config = {key: 1 for key in keys}
    
    status_str, status_code = AdvancedPosition.get_config_status(config)
    
    assert exp_status_str in status_str
    assert status_code == exp_status_code



def test_advanced_dump_config_hook(advanced):
    
    mock = {'clean_existing_dir': True}
    test = advanced.dump_config_hook(mock)
    
    assert test['clean_existing_dir'] is None
