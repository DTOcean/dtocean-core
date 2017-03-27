# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 10:39:38 2015

@author: 108630
"""

import os
    
test_data = {'project.lifetime': 20,
             'project.discount_rate': 0.05
             }
             
if __name__ == "__main__":
    
    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)
    
    print "generate test data: {}".format(pkl_path)
