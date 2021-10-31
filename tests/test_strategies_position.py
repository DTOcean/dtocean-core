# -*- coding: utf-8 -*-

import os

import pytest

from dtocean_core.strategies.position import AdvancedPosition


@pytest.fixture()
def advanced():
    return AdvancedPosition()


def test_advanced_get_name():
    assert AdvancedPosition.get_name() == "Advanced Positioning"


def test_advanced_get_config_fname():
    assert AdvancedPosition.get_config_fname() == "config.yaml"


def test_advanced_dump_config_hook(advanced):
    
    mock = {'clean_existing_dir': True}
    test = advanced.dump_config_hook(mock)
    
    assert test['clean_existing_dir'] is None


def test_advanced_get_variables(advanced):
    assert advanced.get_variables() == ['options.user_array_layout',
                                        'project.rated_power']


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


def test_advanced_configure(mocker, advanced):
    
    mocker.patch.object(advanced,
                        "get_config_status",
                        return_value=[None, 1],
                        autospec=True)
    
    test = {"mock": "mock"}
    advanced.configure(**test)
    
    assert advanced._config == test


def test_advanced_configure_missing_keys(mocker, advanced):
    
    mocker.patch.object(advanced,
                        "get_config_status",
                        return_value=[None, 0],
                        autospec=True)
    
    test = {"mock": "mock"}
    
    with pytest.raises(ValueError) as excinfo:
        advanced.configure(**test)
    
    assert "Required keys are missing" in str(excinfo)


def test_advanced_get_worker_directory_status_missing(tmpdir):
    
    config = {"worker_dir": os.path.join(str(tmpdir), "mock")}
    (status_str,
     status_code) = AdvancedPosition.get_worker_directory_status(config)
    
    assert status_code == 1
    assert "does not yet exist" in status_str


def test_advanced_get_worker_directory_status_empty(tmpdir):
    
    p = tmpdir.mkdir("mock")
    config = {"worker_dir": str(p)}
    (status_str,
     status_code) = AdvancedPosition.get_worker_directory_status(config)
    
    assert status_code == 1
    assert "empty" in status_str


@pytest.mark.parametrize("clean_existing_dir, expected", [
                         (False,              0),
                         (True,               2)])
def test_advanced_get_worker_directory_status_contains_files(
                                                            tmpdir,
                                                            clean_existing_dir,
                                                            expected):
    
    p = tmpdir.mkdir("mock")
    f = p.join("hello.txt")
    f.write("content")
    
    config = {"worker_dir": str(p),
              "clean_existing_dir": clean_existing_dir}
    (status_str,
     status_code) = AdvancedPosition.get_worker_directory_status(config)
    
    assert status_code == expected
    assert "contains files" in status_str


def test_advanced_get_optimiser_status_none(tmpdir):
    
    config = {"worker_dir": os.path.join(str(tmpdir), "mock")}
    (status_str,
     status_code) = AdvancedPosition.get_optimiser_status(None, config)
    
    assert status_code == 0
    assert status_str is None


def test_advanced_get_optimiser_status_complete(tmpdir):
    
    p = tmpdir.join("mock_results.pkl")
    p.write("content")
    
    config = {"worker_dir": str(tmpdir),
              "root_project_path": os.path.join(str(tmpdir), "mock.prj")}
    (status_str,
     status_code) = AdvancedPosition.get_optimiser_status(None, config)
    
    assert status_code == 1
    assert "complete" in status_str


def test_advanced_get_optimiser_status_incomplete(mocker, tmpdir):
    
    mock_opt = mocker.patch("dtocean_core.strategies.position."
                            "PositionOptimiser",
                            autospec=True)
    mock_opt.is_restart.return_value = True
    
    config = {"worker_dir": str(tmpdir),
              "root_project_path": os.path.join(str(tmpdir), "mock.prj")}
    (status_str,
     status_code) = AdvancedPosition.get_optimiser_status(None, config)
    
    assert status_code == 2
    assert "incomplete" in status_str
