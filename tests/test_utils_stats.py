# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 09:55:13 2017

@author: mtopper
"""

import pytest

import numpy as np
from scipy.stats import norm

from dtocean_core.utils.stats import UniVariateKDE


@pytest.fixture(scope="module")
def gaussian():
    
    """Build an estimate of a gaussian distribution. Object is shared"""
    
    data = np.random.normal(size=10000)
    distribution = UniVariateKDE(data)
    
    return distribution


@pytest.fixture
def gaussian_fresh():
    
    """Build an estimate of a gaussian distribution. Object is recreated"""
    
    data = np.random.normal(size=10000)
    distribution = UniVariateKDE(data)
    
    return distribution


def test_pdf(gaussian):
    
    values = np.linspace(-5, 5, 200)
    estimated = gaussian.pdf(values)
    ideal = norm.pdf(values)

    assert np.isclose(estimated, ideal,  rtol=0, atol=5e-02).all()
    
    
def test_cdf(gaussian):
    
    values = np.linspace(-5, 5, 200)
    estimated = gaussian.cdf(values)
    ideal = norm.cdf(values)
        
    assert np.isclose(estimated, ideal,  rtol=0, atol=5e-02).all()
    
    
def test_ppf(gaussian):
    
    probs = np.linspace(0.01, 0.99, 200)
    estimated = gaussian.ppf(probs)
    ideal = norm.ppf(probs)

    assert np.isclose(estimated, ideal,  rtol=0, atol=2e-1).all()
    

def test_mean(gaussian):
    
    """Trival function calculates mean of initial dataset not distribution"""
    
    assert np.isclose(gaussian.mean(), 0.,  rtol=0, atol=1e-1)
    
    
def test_mode(gaussian):
        
    assert np.isclose(gaussian.mode(), 0.,  rtol=0, atol=1e-1)
    
    
def test_interval(gaussian):
    
    estimated = gaussian.confidence_interval(90)
    ideal = norm.interval(0.9)
    
    assert np.isclose(estimated, ideal,  rtol=0, atol=2e-1).all()
    
    
def test_ppf_x0(gaussian):
    
    probs = np.linspace(0.01, 0.99, 200)
    estimated = gaussian.ppf(probs)

    assert estimated.all()

    
def test_interval_x0(gaussian):
    
    estimated = gaussian.confidence_interval(90)
    
    assert estimated.all()
    
    
def test_ppf_fresh(gaussian_fresh):
    
    probs = np.linspace(0.01, 0.99, 200)
    estimated = gaussian_fresh.ppf(probs)
    ideal = norm.ppf(probs)

    assert np.isclose(estimated, ideal,  rtol=0, atol=2e-1).all()

    
def test_interval_fresh(gaussian_fresh):
    
    estimated = gaussian_fresh.confidence_interval(90)
    ideal = norm.interval(0.9)
    
    assert np.isclose(estimated, ideal,  rtol=0, atol=2e-1).all()
