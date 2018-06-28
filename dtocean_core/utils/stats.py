# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 08:49:07 2017

@author: mtopper
"""

import numpy as np

from scipy import optimize, stats
from contours.quad import QuadContourGenerator


class UniVariateKDE(object):
    
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


class BiVariateKDE(object):
    
    def __init__(self, x, y):
        
        self.x = x
        self.y = y
        self.kernel = None
        
        # Populate the kernel
        self._set_kernel()
        
        return
        
    def _set_kernel(self):
        
        values = np.vstack([self.x, self.y])
        self.kernel = stats.gaussian_kde(values)
                
        return
    
    def mode(self, xtol=0.0001, ftol=0.0001, disp=False):
        """Determine the ordinate of the most likely value of the given KDE"""
        
        medians = np.median(self.kernel.dataset, 1)
        
        neg_kde = lambda x: -1 * self.kernel(x)
        modal_coords = optimize.fmin(neg_kde,
                                     medians,
                                     xtol=xtol,
                                     ftol=ftol,
                                     disp=disp)
            
        return modal_coords
    
    def pdf(self, x_range=None, y_range=None, npoints=1000):
        
        # Wide estimate on the ranges if not given
        if x_range is None:
            
            dx = self.x.max() - self.x.min()
            x_range = (self.x.min() - dx, self.x.max() + dx)
                        
        if y_range is None:
            
            dy = self.y.max() - self.y.min()
            y_range = (self.y.min() - dy, self.y.max() + dy)
        
        X, Y = np.mgrid[x_range[0]:x_range[1]:(npoints * 1j),
                        y_range[0]:y_range[1]:(npoints * 1j)]
        positions = np.vstack([X.ravel(), Y.ravel()])
        
        xx = X[:,0]
        yy = Y[0,:]
        pdf = np.reshape(self.kernel(positions).T, X.shape)
        
        return xx, yy, pdf


def pdf_confidence_densities(pdf, levels=None):
    """Determine the required density values to satisfy a list of confidence
    levels in the given pdf"""
    
    def diff_frac(density, pdf, target_frac, pdf_sum):
        density_frac = pdf[pdf >= density].sum() / pdf_sum
        return density_frac - target_frac
    
    if levels is None:
        levels = np.array([95.])
    else:
        levels = np.array(levels)
    
    fracs = levels / 100.
    pdf_sum = pdf.sum()
    densities = []
    
    for frac in fracs:
        
        density = optimize.brentq(diff_frac,
                                  pdf.min(),
                                  pdf.max(),
                                  args=(pdf, frac, pdf_sum))
        
        densities.append(density)
        
    return densities


def pdf_contour_coords(xx, yy, pdf, level):

    c = QuadContourGenerator.from_rectilinear(xx, yy, pdf.T)
    levelc = c.contour(level)
    
    cx = []
    cy = []

    for v in levelc:
        cx.extend(v[:,0])
        cy.extend(v[:,1])
        
    return cx, cy
        
