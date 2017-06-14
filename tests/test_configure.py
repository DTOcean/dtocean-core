
from polite.paths import Directory
from dtocean_core import (start_logging,
                          init_config,
                          init_config_parser,
                          init_config_interface)


def test_init_config(mocker, tmpdir):

    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_core.UserDataDirectory',
                 return_value=mock_dir)
                 
    init_config()
        
    assert len(config_tmpdir.listdir()) == 3
              
              
def test_init_config_parser():
    
    overwrite = init_config_parser([])
    
    assert not overwrite


def test_init_config_parser_overwrite():
    
    overwrite = init_config_parser(["--overwrite"])
    
    assert overwrite
    
    
def test_init_config_interface(mocker, tmpdir):

    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_core.UserDataDirectory',
                 return_value=mock_dir)
    mocker.patch('dtocean_core.init_config_parser',
                 return_value=False)
                 
    init_config_interface()
        
    assert len(config_tmpdir.listdir()) == 3

    
def test_start_logging(mocker, tmpdir):
    
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_core.UserDataDirectory',
                 return_value=mock_dir)

    start_logging()
    
    assert True


def test_start_logging_user(mocker, tmpdir):
    
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_core.UserDataDirectory',
                 return_value=mock_dir)
                 
    init_config()
    
    mocker.patch('dtocean_core.ObjDirectory',
                 return_value=None)
    
    start_logging()
    
    assert True
