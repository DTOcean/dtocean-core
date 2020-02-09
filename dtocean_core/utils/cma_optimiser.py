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
from copy import deepcopy
from subprocess import Popen

import cma
import numpy as np
import yaml

from ..core import Core

# Set up logging
module_logger = logging.getLogger(__name__)


class NormScaler(object):
    
    sigma = 1.
    range_n_sigmas = 3
    
    def __init__(self, range_min, range_max, x0=None):
        
        if x0 is None:
            x0 = 0.5 * (range_min + range_max)
        
        self._scale_factor = _get_scale_factor(range_min,
                                               range_max,
                                               x0,
                                               self.sigma,
                                               self.range_n_sigmas)
        self._x0 = self.scaled(x0)
        
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
    
    def __init__(self, search_dict=None):
        
        if search_dict is None or not search_dict:
            iteration = 0
            search_dict = {}
        else:
            iteration = max(search_dict) + 1
        
        self._iteration = iteration
        self._search_dict = search_dict
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
    
    def copy_search_dict(self):
        
        self._lock.acquire()
        
        try:
            result = deepcopy(self._search_dict)
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
                       restart=False,
                       clean_existing_dir=False):
        
        self._counter = counter
        self._root_project_base_name = root_project_base_name
        self._worker_directory = worker_directory
        self._base_project = base_project
        self._base_penalty = base_penalty
        self._logging = logging
        self._core = Core()
        
        if not restart:
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
    def get_worker_cost(self, results):
        """Return the function cost based on the data read from the worker
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
    def cleanup(self, worker_project_path, flag, results):
        """Hook to clean up simulation files as required"""
        return
    
    def get_counter_search_dict(self):
        
        return self._counter.copy_search_dict()
    
    def _print_exception(self, e, flag):
        
        print flag
        print e
        
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  file=sys.stdout)
        
        return
    
    def _log_exception(self, e, flag):
        
        module_logger.debug(flag)
        module_logger.debug(e)
        
        exc_type, exc_value, exc_traceback = sys.exc_info()
        msg_strs = traceback.format_exception(exc_type,
                                              exc_value,
                                              exc_traceback)
        msg_str = ''.join(msg_strs)
        module_logger.debug(msg_str)
        
        return
    
    def _iterate(self, results_queue, *args):
        
        previous_cost = self._counter.get_cost(*args)
        
        if previous_cost:
            results_queue.put(previous_cost)
            return
        
        flag = ""
        iteration = self._counter.get_iteration()
        cost = None
        
        worker_file_root_path = "{}_{}".format(self._root_project_base_name,
                                               iteration)
        worker_project_name = "{}.prj".format(worker_file_root_path)
        worker_results_name = "{}.yaml".format(worker_file_root_path)
        worker_project_path = os.path.join(self._worker_directory,
                                           worker_project_name)
        worker_results_path = os.path.join(self._worker_directory,
                                           worker_results_name)
        
        results = None
        
        try:
            
            self._core.dump_project(self._base_project, worker_project_path)
            
        except Exception as e:
            
            cost = -1
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
                
                args_str = ", ".join(popen_args)
                err_str = ("External process failed to open. Arguments were: "
                           "{}").format(args_str)
                
                raise RuntimeError(err_str)
        
        except Exception as e:
            
            cost = -1
            flag = "Fail Execute"
            worker_results_path = None
            
            if self._logging == "print":
                self._print_exception(e, flag)
            elif self._logging == "module":
                self._log_exception(e, flag)
        
        if "Fail" not in flag:
            
            try:
                
                with open(worker_results_path, "r") as stream:
                    results = yaml.load(stream, Loader=yaml.FullLoader)
                
                cost = self.get_worker_cost(results)
            
            except Exception as e:
                
                cost = -1
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
        self.cleanup(worker_project_path, flag, results)
        
        results_queue.put(cost)
        
        return
    
    def __call__(self, q):
        
        while True:
            
            item = q.get()
            self._iterate(*item)
            q.task_done()
            
        return


class Main(object):
    
    def __init__(self, es,
                       worker_directory,
                       iterator,
                       scaled_vars,
                       nearest_ops,
                       fixed_index_map=None,
                       num_threads=1,
                       logging="module"):
        
        self.es = es
        self.iterator = iterator
        self.stop = False
        self._worker_directory = worker_directory
        self._scaled_vars = scaled_vars
        self._nearest_ops = nearest_ops
        self._fixed_index_map = fixed_index_map
        self._num_threads = num_threads
        self._logging = logging
        self._thread_queue = None
    
    def init_threads(self):
            
        self._thread_queue = queue.Queue()
        
        for i in range(self._num_threads):
            
            worker = threading.Thread(target=self.iterator,
                                      args=(self._thread_queue,))
            worker.setDaemon(True)
            worker.start()
        
        return
    
    def next(self):
        
        if self.es.stop():
            self.stop = True
            return
        
        final_solutions = []
        final_costs = []
        
        while len(final_solutions) < self.es.popsize:
            
            result_queue = queue.Queue()
            needed_solutions = self.es.popsize - len(final_solutions)
            run_solutions = []
            run_descaled_solutions = []
            
            while len(run_solutions) < needed_solutions:
                
                ask_solutions = needed_solutions - len(run_solutions)
                scaled_solutions = self.es.ask(ask_solutions)
                descaled_solutions = []
                
                for solution in scaled_solutions:
                    
                    new_solution = [scaler.inverse(x) for x, scaler
                                        in zip(solution, self._scaled_vars)]
                    nearest_solution = [snap(x) for x, snap
                                    in zip(new_solution, self._nearest_ops)]
                    descaled_solutions.append(nearest_solution)
                
                if self._fixed_index_map is not None:
                    
                    ordered_index_map = OrderedDict(
                                        sorted(self._fixed_index_map.items(),
                                               key=lambda t: t[0]))
                    
                    for solution in descaled_solutions:
                        for idx, val in ordered_index_map.iteritems():
                            solution.insert(idx, val)
                
                checked_solutions = []
                checked_descaled_solutions = []
                
                for sol, des_sol in zip(scaled_solutions, descaled_solutions):
                    if self.iterator.pre_constraints_hook(*des_sol): continue
                    checked_solutions.append(sol)
                    checked_descaled_solutions.append(des_sol)
                
                run_solutions.extend(checked_solutions)
                run_descaled_solutions.extend(checked_descaled_solutions)
            
            run_idxs, match_dict = _get_match_process(run_descaled_solutions)
            
            for i in run_idxs:
                self._thread_queue.put([result_queue] +
                                                   run_descaled_solutions[i])
            
            self._thread_queue.join()
            
            costs = _rebuild_input(result_queue.queue,
                                   run_idxs,
                                   match_dict,
                                   len(run_descaled_solutions))
            
            valid_solutions = []
            valid_costs = []
            
            for sol, cost in zip(run_solutions, costs):
                
                if cost < 0.: continue
                valid_solutions.append(sol)
                valid_costs.append(cost)
            
            final_solutions.extend(valid_solutions)
            final_costs.extend(valid_costs)
        
        self.es.tell(final_solutions, final_costs)
        self.es.logger.add()
        self.es.disp()
        
        if self._logging == "print":
            self.es.disp()
        elif self._logging == "module":
            msg_str = ('Minimum fitness for iteration {}: '
                       '{:.15e}').format(self.es.countiter,
                        min(self.es.fit.fit))
            module_logger.info(msg_str)
        
        return


def init_evolution_strategy(x0,
                            low_bound,
                            high_bound,
                            max_simulations=None,
                            popsize=None,
                            timeout=None):
    
    opts = {'bounds': [low_bound, high_bound]}#,
#            'verbose': -3}
    
    if max_simulations is not None:
        opts["maxfevals"] = max_simulations
    
    if popsize is not None:
        opts["popsize"] = popsize
    
    if timeout is not None:
        opts["timeout"] = timeout
    
    es = cma.CMAEvolutionStrategy(x0, NormScaler.sigma, opts)
    
    return es


def dump_outputs(es, iterator, worker_directory):
    
    counter_dict = iterator.get_counter_search_dict()
    
    es_fname = os.path.join(worker_directory, 'saved-cma-object.pkl')
    counter_dict_fname = os.path.join(worker_directory,
                                      'saved-counter-search-dict.pkl')
    
    pickle.dump(es, open(es_fname, 'wb'), -1)
    pickle.dump(counter_dict, open(counter_dict_fname, 'wb'), -1)
    
    return


def load_outputs(worker_directory):
    
    es_fname = os.path.join(worker_directory, 'saved-cma-object.pkl')
    counter_dict_fname = os.path.join(worker_directory,
                                      'saved-counter-search-dict.pkl')
    
    es = pickle.load(open(es_fname, 'rb'))
    counter_dict = pickle.load(open(counter_dict_fname, 'rb'))
    
    return es, counter_dict


def _get_scale_factor(range_min, range_max, x0, sigma, n_sigmas):
    
    if x0 < range_min or x0 > range_max:
        err_str = "x0 must lie between range_min and range_max"
        raise ValueError(err_str)
    
    if sigma <= 0:
        err_str = "sigma must be positive"
        raise ValueError(err_str)
    
    if n_sigmas % 1 != 0 or int(n_sigmas) <= 0:
        err_str = "n_sigmas must a positive whole number"
        raise ValueError(err_str)
    
    max_half_range = max(range_max - x0, x0 - range_min)
    half_scaled_range = sigma * int(n_sigmas)
    
    return half_scaled_range / max_half_range


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
