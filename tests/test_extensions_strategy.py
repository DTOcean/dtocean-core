
import pytest

from dtocean_core.extensions import StrategyManager


@pytest.fixture(scope="module")
def manager():
    
    return StrategyManager()
    
    
def test_get_available(manager):
    
    result = manager.get_available()
    
    assert len(result) > 0
    
    
def test_get_strategy(manager):
    
    strategies = manager.get_available()
    
    for strategy_name in strategies:
        manager.get_strategy(strategy_name)
        
    assert True
