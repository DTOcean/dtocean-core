# -*- coding: utf-8 -*-

"""
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import os
import abc
import sys
import queue
import pickle
import logging
import threading
import traceback
from collections import OrderedDict
from subprocess import Popen

import cma
import numpy as np

from ..core import Core

# Set up logging
module_logger = logging.getLogger(__name__)


class NormScaler(object):
    
    sigma = 1.
    range_n_sigmas = 3
    
    def __init__(self, range_min, range_max):
        
        self._scale_factor = _get_scale_factor(range_min,
                                               range_max,
                                               self.sigma,
                                               self.range_n_sigmas)
        self._x0 = self.scaled(0.5 * (range_min + range_max))
        
        return
    
    @property
    def x0(self):
        return self._x0
    
    def scaled(self, value):
        return value * self._scale_factor
    
    def inverse(self, value):
        return value / self._scale_factor


class Counter(object):
    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self):
        
        self._iteration = 0
        self._search_dict = {}
        self._lock = threading.Lock()
        
        return
    
    def set_params(self, iteration, *args):
        
        params = self._set_params(*args)
        
        self._lock.acquire()
        
        try:
            
            if iteration in self._search_dict:
                err_str = ("Iteration {} has already been "
                           "recorded").format(iteration)
                raise ValueError(err_str)
                
            self._search_dict[iteration] = params
        
        finally:
            
            self._lock.release()
        
        return
    
    @abc.abstractmethod
    def _set_params(self, *args):
        """Build a params (probably namedtuple) object to search against."""
        return
    
    def get_cost(self, *args):
        
        self._lock.acquire()
        cost = None
        
        try:
            
            for params in self._search_dict.values():
                cost = self._get_cost(params, *args)
                if cost is not None: break
        
        finally:
            
            self._lock.release()
        
        if cost is None: cost = False
        
        return cost
    
    @abc.abstractmethod
    def _get_cost(self, params, *args):
        """Return cost if parameters in params object match input args, else
        return None."""
        return
    
    def get_iteration(self):
        
        self._lock.acquire()
        
        try:
            
            result = self._iteration
            self._iteration += 1
        
        finally:
            
            self._lock.release()
        
        return result


class Iterator(object):
    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, root_project_base_name,
                       worker_directory,
                       base_project,
                       counter,
                       base_penalty=1.,
                       logging="module",
                       clean_existing_dir=False):
        
        self._counter = counter
        self._root_project_base_name = root_project_base_name
        self._worker_directory = worker_directory
        self._base_project = base_project
        self._base_penalty = base_penalty
        self._logging = logging
        self._core = Core()
        
        _clean_directory(worker_directory, clean_existing_dir)
        
        return
    
    @abc.abstractmethod
    def get_popen_args(self, worker_project_path, *args):
        "Return the arguments to create a new process thread using Popen"
        return
    
    @abc.abstractmethod
    def pre_constraints_hook(self, *args):
        """Allows checking of constraints prior to execution. Should return
        None if not violated otherwise return cost"""
        return
    
    @abc.abstractmethod
    def get_worker_cost(self, lines):
        """Return the function cost based on the lines read from the worker
        results file."""
        return
    
    @abc.abstractmethod
    def set_counter_params(self, iteration,
                                 worker_project_path,
                                 worker_results_path,
                                 cost,
                                 flag,
                                 *args):
        """Update the counter object with new data."""
        return
    
    @abc.abstractmethod
    def cleanup(self, worker_project_path, flag, lines):
        """Hook to clean up simulation files as required"""
        return
    
    def _print_exception(self, e, flag):
        
        print e
        print flag
        
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  file=sys.stdout)
        
        return
    
    def _log_exception(self, e, flag):
        
        module_logger.debug(e)
        module_logger.debug(flag)
        
        exc_type, exc_value, exc_traceback = sys.exc_info()
        msg_str = traceback.format_exception(exc_type,
                                             exc_value,
                                             exc_traceback)
        module_logger.debug(msg_str)
        
        return
    
    def _iterate(self, results_queue, *args):
        
        previous_cost = self._counter.get_cost(*args)
        
        if previous_cost:
            results_queue.put(previous_cost)
            return
        
        pre_constraint_cost = self.pre_constraints_hook(*args)
        
        if pre_constraint_cost is not None:
            results_queue.put(pre_constraint_cost)
            return
        
        iteration = self._counter.get_iteration()
    
        worker_file_root_path = "{}_{}".format(self._root_project_base_name,
                                               iteration)
        worker_project_name = "{}.prj".format(worker_file_root_path)
        worker_results_name = "{}.dat".format(worker_file_root_path)
        worker_project_path = os.path.join(self._worker_directory,
                                           worker_project_name)
        worker_results_path = os.path.join(self._worker_directory,
                                           worker_results_name)
        
        flag = ""
        lines = None
        
        try:
            
            self._core.dump_project(self._base_project, worker_project_path)
            
        except Exception as e:
            
            cost = self._base_penalty
            flag = "Fail Send"
            worker_results_path = None
            
            if self._logging == "print":
                self._print_exception(e, flag)
            elif self._logging == "module":
                self._log_exception(e, flag)
        
        try:
            
            popen_args = self.get_popen_args(worker_project_path, *args)
            process = Popen(popen_args, close_fds=True)
            exit_code = process.wait()
            
            if exit_code != 0:
                
                args_str = ",".join(popen_args)
                err_str = ("External process failed to open. Arguments were: "
                           "{}").format(args_str)
                
                raise RuntimeError(err_str)
        
        except Exception as e:
            
            cost = self._base_penalty
            flag = "Fail Execute"
            worker_results_path = None
            
            if self._logging == "print":
                self._print_exception(e, flag)
            elif self._logging == "module":
                self._log_exception(e, flag)
        
        if "Fail" not in flag:
            
            try:
                
                with open(worker_results_path, "r") as f:
                    lines = f.read().splitlines()
                
                cost = self.get_worker_cost(lines)
            
            except Exception as e:
                
                cost = self._base_penalty
                flag = "Fail Receive"
                worker_results_path = None
            
                if self._logging == "print":
                    self._print_exception(e, flag)
                elif self._logging == "module":
                    self._log_exception(e, flag)
        
        self.set_counter_params(iteration,
                                worker_project_path,
                                worker_results_path,
                                cost,
                                flag,
                                *args)
        self.cleanup(worker_project_path, flag, lines)
        
        results_queue.put(cost)
        
        return
    
    def __call__(self, q):
    
        while True:
            
            item = q.get()
            self._iterate(*item)
            q.task_done()
            
        return


def _get_scale_factor(range_min, range_max, sigma, n_sigmas):
    
    init_range = range_max - range_min
    scaled_range = 2. * sigma * n_sigmas
    
    return scaled_range / init_range


def _clean_directory(dir_name, clean_existing=False, logging="module"):
    
    if not os.path.exists(dir_name):
        
        os.makedirs(dir_name)
        
    else:
        
        if not clean_existing:
            
            err_msg = ("Directory {} already exists. Set clean_existing "
                       "argument to True to delete the contents of the "
                       "directory").format(dir_name)
            raise IOError(err_msg)
        
        for the_file in os.listdir(dir_name):
            file_path = os.path.join(dir_name, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                #elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                if logging == "print":
                    print(e)
                elif logging == "module":
                    module_logger.debug(e)
    
    return


def main(worker_directory,
         iterator,
         x0,
         low_bound,
         high_bound,
         scaled_vars,
         nearest_ops,
         fixed_index_map=None,
         num_threads=5,
         max_simulations=None,
         logging="module"):
    
    opts = {'bounds': [low_bound, high_bound],
            'verbose': -3}
    
    if max_simulations is not None:
        opts["maxfevals"] = max_simulations
    
    es = cma.CMAEvolutionStrategy(x0, NormScaler.sigma, opts)
    
    _store_outputs(es, iterator, worker_directory)
    
    thread_queue = queue.Queue()
    
    for i in range(num_threads):
        
        worker = threading.Thread(target=iterator,
                                  args=(thread_queue,))
        worker.setDaemon(True)
        worker.start()
    
    while not es.stop() and not os.path.isfile('pause_optimiser.txt'):
        
        result_queue = queue.Queue()
        scaled_solutions = es.ask()
        descaled_solutions = []
        
        for solution in scaled_solutions:
            
            new_solution = [scaler.inverse(x) for x, scaler
                                            in zip(solution, scaled_vars)]
            nearest_solution = [snap(x) for x, snap
                                            in zip(new_solution, nearest_ops)]
            descaled_solutions.append(nearest_solution)
        
        if fixed_index_map is not None:
            
            ordered_index_map = OrderedDict(sorted(fixed_index_map.items(),
                                                   key=lambda t: t[0]))
            
            for solution in descaled_solutions:
                for idx, val in ordered_index_map.iteritems():
                    solution.insert(idx, val)
        
        run_idxs, match_dict = _get_match_process(descaled_solutions)
        
        for i in run_idxs:
            thread_queue.put([result_queue] + descaled_solutions[i])
        
        thread_queue.join()
        
        costs = _rebuild_input(result_queue.queue,
                               run_idxs,
                               match_dict,
                               len(descaled_solutions))
        
        es.tell(scaled_solutions, costs)
        
        if logging == "print":
            es.disp()
        elif logging == "module":
            msg_str = ('Minimum fitness for iteration {}: '
                       '{:.15e}').format(es.countiter, min(es.fit.fit))
            module_logger.info(msg_str)
        
        _store_outputs(es, iterator, worker_directory)
    
    return es


def _get_match_process(values):
    
    match_dict = {}
    all_matches = []
    
    for i in range(len(values) - 1):
        
        if i in all_matches: continue
        
        key = i
        base = values[i]
        match_list = []
        
        for j in range(i + 1, len(values)):
            
            test = values[j]
            
            if all([x == y for x, y in zip(base, test)]):
                match_list.append(j)
        
        all_matches.extend(match_list)
        
        if match_list: match_dict[key] = match_list
    
    process_set = set(range(len(values))) - set(all_matches)
    
    return list(process_set), match_dict


def _rebuild_input(values, run_idxs, match_dict, input_length):
    
    rebuild = np.zeros(input_length)
    
    for idx, res in zip(run_idxs, values):
        rebuild[idx] = res
    
    for base_idx, copy_idxs in match_dict.iteritems():
        rebuild[copy_idxs] = rebuild[base_idx]
    
    return rebuild


def _store_outputs(es, iterator, worker_directory):
    
    counter_dict = iterator._counter._search_dict
    
    es_fname = os.path.join(worker_directory, 'saved-cma-object.pkl')
    counter_dict_fname = os.path.join(worker_directory,
                                      'saved-counter-search-dict.pkl')
    
    pickle.dump(es, open(es_fname, 'wb'))
    pickle.dump(counter_dict, open(counter_dict_fname, 'wb'))
    
    return
