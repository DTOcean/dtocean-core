
import os
import shutil
import zipfile
from stat import S_IREAD, S_IRGRP, S_IROTH

import pytest

from dtocean_core.utils.files import unpack_archive, onerror


def test_unpack_archive_zip(tmpdir):
    
    src_path = os.path.join(str(tmpdir), 'zipfile_write.zip')
    dst_path = os.path.join(str(tmpdir), 'test')
    
    readme = tmpdir.join('README.txt')
    readme.write("test")

    zf = zipfile.ZipFile(src_path, mode='w')
    
    try:
        zf.write(str(readme))
    finally:
        zf.close()
    
    unpack_archive(src_path, dst_path)

    assert len(os.listdir(dst_path)) == 1


def test_onerror(tmpdir):
    
    config_tmpdir = tmpdir.mkdir("config")
    test_file = config_tmpdir.join("locked.file")
    test_file.write('a')
    
    os.chmod(str(test_file), S_IREAD|S_IRGRP|S_IROTH)
    
    assert len(os.listdir(str(tmpdir))) == 1
    
    with pytest.raises(Exception):
        shutil.rmtree(str(config_tmpdir))
        
    assert len(os.listdir(str(tmpdir))) == 1
    
    shutil.rmtree(str(config_tmpdir), onerror=onerror)
    
    assert len(os.listdir(str(tmpdir))) == 0
