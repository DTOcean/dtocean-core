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
        
        return
    
    def pdf(self, values):
        
        return self._kde(values)
    
    def cdf(self, values):
        
        if self._cdf is None:
            self._cdf = self._calc_cdf()
            
        return self._cdf(values)
    
    def ppf(self, probabilities):
        
        if self._ppf is None:
            self._ppf = self._calc_ppf()
            
        return self._ppf(probabilities)

    def mean(self):
        
        return self._kde.dataset.mean()
    
    def mode(self, samples=1000):
        
        """Numerically search for the mode"""
        
        x = np.linspace(self._kde.dataset.min(),
                        self._kde.dataset.max(),
                        samples)
        most_likely = x[np.argsort(self._kde(x))[-1]]
        
        return most_likely
    
    def confidence_interval(self, percent):
        
        if self._ppf is None:
            self._ppf = self._calc_ppf()
            
        x = percent / 100.
        bottom = (1 - x) / 2
        top = (1 + x) / 2
        
        return self._ppf([bottom, top])
        
    def _calc_cdf(self):
        
        def _kde_cdf(x):
            return self._kde.integrate_box_1d(-np.inf, x)
        
        kde_cdf = np.vectorize(_kde_cdf)
        
        return kde_cdf
    
    def _calc_ppf(self):
        
        if self._cdf is None:
            self._cdf = self._calc_cdf()
        
        def _kde_ppf(q):
            return optimize.fsolve(lambda x, q: self._cdf(x) - q,
                                   0.,
                                   args=(q,))[0]
                           
        kde_ppf = np.vectorize(_kde_ppf)
        
        return kde_ppf
