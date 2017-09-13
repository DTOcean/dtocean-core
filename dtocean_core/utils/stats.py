# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 08:49:07 2017

@author: mtopper
"""

import numpy as np
from scipy import optimize, stats


class EstimatedDistribution(object):
    
    def __init__(self, data, bandwidth=0.3):
        
        self._kde = stats.gaussian_kde(data, bw_method=bandwidth)
        self._cdf = None
        self._ppf = None
        self._x0 = 0.
        
        return
    
    def pdf(self, values):
        
        return self._kde(values)
    
    def cdf(self, values):
        
        if self._cdf is None:
            self._cdf = self._calc_cdf()
            
        return self._cdf(values)
    
    def ppf(self, probabilities, x0=None):
        
        if self._ppf is None or self._x0 != x0:
            self._ppf = self._calc_ppf(x0)
            self._x0 = x0
            
        result = self._ppf(probabilities)
        
        if np.isnan(result).any(): result = None

        return result

    def mean(self):
        
        return self._kde.dataset.mean()
    
    def mode(self, samples=1000):
        
        """Numerically search for the mode"""
        
        x = np.linspace(self._kde.dataset.min(),
                        self._kde.dataset.max(),
                        samples)
        most_likely = x[np.argsort(self._kde(x))[-1]]
        
        return most_likely
    
    def confidence_interval(self, percent, x0=None):
        
        if self._ppf is None:
            self._ppf = self._calc_ppf(x0)
            
        x = percent / 100.
        bottom = (1 - x) / 2
        top = (1 + x) / 2
        
        result = self._ppf([bottom, top])
        
        if np.isnan(result).any(): result = None
        
        return result
        
    def _calc_cdf(self):
        
        def _kde_cdf(x):
            return self._kde.integrate_box_1d(-np.inf, x)
        
        kde_cdf = np.vectorize(_kde_cdf)
        
        return kde_cdf
    
    def _calc_ppf(self, x0=None):
        
        if self._cdf is None:
            self._cdf = self._calc_cdf()
        
        def _kde_ppf(q):
            
            x0_list = [self.mean(),
                       0.,
                       self._kde.dataset.min(),
                       self._kde.dataset.max()]
            
            if x0 is not None: x0_list = [x0] + x0_list
            
            for x0_local in x0_list:
            
                result = optimize.fsolve(lambda x, q: self._cdf(x) - q,
                                         x0_local,
                                         args=(q,),
                                         full_output=True)
                
                if result[2] == 1: return result[0]
                            
            return np.nan
                           
        kde_ppf = np.vectorize(_kde_ppf)
        
        return kde_ppf
