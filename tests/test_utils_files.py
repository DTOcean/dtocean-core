
import os
import shutil
from stat import S_IREAD, S_IRGRP, S_IROTH

import pytest

from dtocean_core.utils.files import onerror


def test_onerror(tmpdir):
    
    config_tmpdir = tmpdir.mkdir("config")
    test_file = os.path.join(str(config_tmpdir), "locked.file")
    
    open(test_file, 'a').close()
    os.chmod(test_file, S_IREAD|S_IRGRP|S_IROTH)
    
    assert len(os.listdir(str(tmpdir))) == 1
    
    with pytest.raises(Exception):
        shutil.rmtree(str(config_tmpdir))
        
    assert len(os.listdir(str(tmpdir))) == 1
    
    shutil.rmtree(str(config_tmpdir), onerror=onerror)
    
    assert len(os.listdir(str(tmpdir))) == 0
