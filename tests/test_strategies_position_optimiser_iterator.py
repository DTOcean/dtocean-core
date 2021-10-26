# -*- coding: utf-8 -*-

import pytest

from dtocean_core.core import OrderedSim, Project, Core
from dtocean_core.menu import ModuleMenu
from dtocean_core.pipeline import Branch
from dtocean_core.strategies.position_optimiser.iterator import (
                                                _get_branch,
                                                prepare)

# Check for module
pytest.importorskip("dtocean_hydro")


def test_get_branch():
    
    core = Core()
    project = Project("mock")
    new_sim = OrderedSim("Default")
    new_sim.set_inspection_level(core._markers["initial"])
    project.add_simulation(new_sim)
    core.register_level(project,
                        core._markers["initial"],
                        None)
    
    core.new_hub(project) # project hub
    core.new_hub(project) # modules hub
    
    branch_name = "Hydrodynamics"
    
    menu = ModuleMenu()
    menu.activate(core, project, branch_name)
    
    test = _get_branch(core, project, branch_name)
    
    assert isinstance(test, Branch)


def test_prepare():
    
    