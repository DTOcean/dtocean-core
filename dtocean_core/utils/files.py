# -*- coding: utf-8 -*-

#    Copyright (C) 2016 'Mathew Topper, Vincenzo Nava, David Bould, Rui Duarte,
#                       'Francesco Ferri, Adam Collin'
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Created on Tue Feb 23 15:38:18 2016

@author: 108630
"""

import os
import shutil
import pickle
import zipfile
import tempfile

def pickle_test_data(file_path, test_data_dict):

    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_root = os.path.splitext(file_name)[0]
    dst_name = "{}.pkl".format(file_root)
    dst_path = os.path.join(dir_path, dst_name)
    
    with open(dst_path, 'wb') as dataf:
    
        # Pickle dictionary using protocol 0.
        pickle.dump(test_data_dict, dataf)
        
    return dst_path
    
def package_dir(src_dir_path, dst_path, archive=False):
    
    if not os.path.splitext(dst_path)[1]: archive = False
    
    if not archive:
        
        for root, dirs, files in os.walk(src_dir_path, topdown=True):
            
            for name in dirs:
                new_path = os.path.join(dst_path, name)
                if os.path.exists(new_path): shutil.rmtree(new_path)
                os.makedirs(new_path)

            for name in files:
                tmp_path = os.path.join(root, name)
                short_path = tmp_path.replace(src_dir_path, "")
                new_path = os.path.join(dst_path, short_path[1:])
                shutil.move(tmp_path, new_path)
                
        shutil.rmtree(src_dir_path)
     
        return

    zip_dir_path = tempfile.mkdtemp()
    
    project_file_name = os.path.split(dst_path)[1]
    zip_file_name = "{}.zip".format(project_file_name)
    zip_file_path = os.path.join(zip_dir_path, zip_file_name)
    
    first = True
        
    for root, dirs, files in os.walk(src_dir_path):

        for name in files:
            
            file_path = os.path.join(root, name)
            short_path = file_path.replace(src_dir_path, "")
                            
            if first:
                mode = "w"
                first = False
            else:
                mode = "a"
            
            zf = zipfile.ZipFile(zip_file_path,
                                 mode,
                                 zipfile.ZIP_DEFLATED)
            
            try:
                zf.write(file_path, arcname=short_path)
            finally:
                zf.close()
    
    shutil.move(zip_file_path, dst_path)
    
    shutil.rmtree(zip_dir_path)
    shutil.rmtree(src_dir_path)
    
    return

