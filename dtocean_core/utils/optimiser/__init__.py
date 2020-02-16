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
from math import ceil
from subprocess import Popen

import cma
import yaml
import numpy as np
from numpy.linalg import norm

from ..files import init_dir
from ...core import Core

# Convenience import
from .noisehandler import NoiseHandler


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
                       logging="module",
                       restart=False,
                       clean_existing_dir=False):
        
        self._counter = counter
        self._root_project_base_name = root_project_base_name
        self._worker_directory = worker_directory
        self._base_project = base_project
        self._logging = logging
        self._core = Core()
        
        if not restart:
            init_dir(worker_directory, clean_existing_dir)
        
        return
    
    @abc.abstractmethod
    def get_popen_args(self, worker_project_path, *args):
        "Return the arguments to create a new process thread using Popen"
        return
    
    @abc.abstractmethod
    def pre_constraints_hook(self, *args):
        """Allows checking of constraints prior to execution. Should return
        True if violated otherwise False"""
        return
    
    @abc.abstractmethod
    def get_worker_cost(self, results):
        """Return the function cost based on the data read from the worker
        results file. Constraint violation should return np.nan"""
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
    
    def _iterate(self, idx, results_queue, *args):
        
        previous_cost = self._counter.get_cost(*args)
        
        if previous_cost:
            results_queue.put((idx, previous_cost))
            return
        
        flag = ""
        iteration = self._counter.get_iteration()
        cost = np.nan
        
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
        
        results_queue.put((idx, cost))
        
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
                       nh=None,
                       fixed_index_map=None,
                       base_penalty=None,
                       num_threads=None,
                       max_resample_loop_factor=None,
                       logging="module"):
        
        # Defaults
        if base_penalty is None: base_penalty = 1.
        if num_threads is None: num_threads = 1
        if max_resample_loop_factor is None: max_resample_loop_factor = 100
        
        if max_resample_loop_factor <= 0:
            err_msg = ("Argument max_resample_loop_factor must be greater "
                       "than zero")
            raise ValueError(err_msg)
        
        max_resample_loops = int(ceil(max_resample_loop_factor * es.popsize))
        
        self.es = es
        self.nh = nh
        self.iterator = iterator
        self._stop = False
        self._worker_directory = worker_directory
        self._scaled_vars = scaled_vars
        self._nearest_ops = nearest_ops
        self._fixed_index_map = fixed_index_map
        self._base_penalty = base_penalty
        self._num_threads = num_threads
        self._max_resample_loops = max_resample_loops
        self._logging = logging
        self._thread_queue = None
        self._sol_feasible = None
        
        self._init_threads()
        
        return
    
    @property
    def stop(self):
        return self._stop
    
    def next(self):
        
        if self.es.stop():
            self._stop = True
            return
        
        if self.nh is None:
            self._next()
        else:
            self._next_nh()
        
        self.es.disp()
        
        if self._logging == "print":
            self.es.disp()
        elif self._logging == "module":
            msg_str = ('Minimum fitness for iteration {}: '
                       '{:.15e}').format(self.es.countiter,
                        min(self.es.fit.fit))
            module_logger.info(msg_str)
        
        return
    
    def _next(self):
        
        final_solutions, final_costs = self._get_solutions_costs(self.es)
        self.es.tell(final_solutions, final_costs)
        self.es.logger.add()
        
        return
    
    def _next_nh(self):
        
        (final_solutions,
         final_costs) = self._get_solutions_costs(self.es,
                                                  self.nh.evaluations)
        self.es.tell(final_solutions, final_costs)
        self._sigma_correction(final_solutions, final_costs)
        self.es.logger.add(more_data=[self.nh.evaluations, self.nh.noiseS])
        
        return
        
    def _init_threads(self):
            
        self._thread_queue = queue.Queue()
        
        for i in range(self._num_threads):
            
            worker = threading.Thread(target=self.iterator,
                                      args=(self._thread_queue,))
            worker.setDaemon(True)
            worker.start()
        
        return
    
    def _sigma_correction(self, final_solutions, final_costs):
        
        self.nh.prepare(final_solutions,
                        final_costs,
                        self.es.ask)
        nh_costs = self._get_nh_costs(self.nh, self.nh.n_evals)
        self.nh.tell(nh_costs)
        self.es.sigma *= self.nh.sigma_fac
        self.es.countevals += self.nh.evaluations_just_done
        
        return
    
    def _get_solutions_costs(self, asktell, n_evals=None):
        
        final_solutions = []
        final_costs = []
        
        while len(final_solutions) < asktell.popsize:
        
            result_queue = queue.Queue()
            needed_solutions = asktell.popsize - len(final_solutions)
            scaled_solutions = None
            run_solutions = []
            run_descaled_solutions = []
            resample_loops = 0
            
            while (len(run_solutions) < needed_solutions):
                
                # If the maximum number of resamples is reached apply a 
                # penalty value to a new set of solutions based on a fixed 
                # penalty and the distance to a previous best solution
                if resample_loops == self._max_resample_loops:
                    
                    if self._sol_feasible is None:
                        
                        if self.es.countiter == 0:
                            err_msg = ("There are no feasible solutions to "
                                       "use for penalty calculation. Problem "
                                       "is likely ill-posed.")
                            raise RuntimeError(err_msg)
                        
                        self._sol_feasible = self.es.best.x.copy()
                    
                    log_msg = ("Maximum of {} resamples reached. Applying "
                               "penalty values.").format(
                                                   self._max_resample_loops)
                    module_logger.info(log_msg)
                    
                    scaled_solutions = asktell.ask(asktell.popsize)
                    
                    costs = [self._base_penalty + norm(
                                        sol - self._sol_feasible)
                                                for sol in scaled_solutions]
                    
                    return scaled_solutions, costs
                
                ask_solutions = needed_solutions - len(run_solutions)
                scaled_solutions = asktell.ask(ask_solutions)
                descaled_solutions = []
                
                for solution in scaled_solutions:
                    
                    new_solution = [scaler.inverse(x) for x, scaler
                                        in zip(solution, self._scaled_vars)]
                    nearest_solution = \
                            [snap(x) if snap is not None else x
                                     for x, snap in zip(new_solution,
                                                        self._nearest_ops)]
                    
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
                
                resample_loops += 1
            
            log_msg = ("{} resample loops required to generate {} "
                       "solutions").format(resample_loops, needed_solutions)
            module_logger.debug(log_msg)
            
            run_idxs, match_dict = _get_match_process(run_descaled_solutions)
            
            for i in run_idxs:
                self._thread_queue.put([i, result_queue] +
                                       run_descaled_solutions[i] + 
                                       [n_evals])
            
            self._thread_queue.join()
            
            costs = _rebuild_input(result_queue.queue,
                                   match_dict,
                                   len(run_descaled_solutions))
            
            valid_solutions = []
            valid_costs = []
            
            for sol, cost in zip(run_solutions, costs):
                
                if np.isnan(cost): continue
                valid_solutions.append(sol)
                valid_costs.append(cost)
            
            final_solutions.extend(valid_solutions)
            final_costs.extend(valid_costs)
        
        return final_solutions, final_costs
    
    def _get_nh_costs(self, asktell, n_evals=None):
        
        result_queue = queue.Queue()
        scaled_solutions = asktell.ask()
        final_costs = np.zeros(asktell.popsize)
        descaled_solutions = []
        
        for solution in scaled_solutions:
            
            new_solution = [scaler.inverse(x) for x, scaler
                                in zip(solution, self._scaled_vars)]
            nearest_solution = \
                    [snap(x) if snap is not None else x
                             for x, snap in zip(new_solution,
                                                self._nearest_ops)]
            
            descaled_solutions.append(nearest_solution)
        
        if self._fixed_index_map is not None:
            
            ordered_index_map = OrderedDict(
                                sorted(self._fixed_index_map.items(),
                                       key=lambda t: t[0]))
            
            for solution in descaled_solutions:
                for idx, val in ordered_index_map.iteritems():
                    solution.insert(idx, val)
        
        run_descaled_solutions = []
        run_descaled_solutions_idxs = []
        
        for i, des_sol in enumerate(descaled_solutions):
            
            if self.iterator.pre_constraints_hook(*des_sol): 
                final_costs[i] = np.nan
            else:
                run_descaled_solutions.append(des_sol)
                run_descaled_solutions_idxs.append(i)
        
        run_idxs, match_dict = _get_match_process(run_descaled_solutions)
        
        for i in run_idxs:
            self._thread_queue.put([i, result_queue] +
                                   run_descaled_solutions[i] + 
                                   [n_evals])
        
        self._thread_queue.join()
        
        costs = _rebuild_input(result_queue.queue,
                               match_dict,
                               len(run_descaled_solutions))
        
        for i, cost in zip(run_descaled_solutions_idxs, costs):
            final_costs[i] = cost
        
        return final_costs



def init_evolution_strategy(x0,
                            low_bound,
                            high_bound,
                            max_simulations=None,
                            popsize=None,
                            timeout=None,
                            tolfun=None):
    
    opts = {'bounds': [low_bound, high_bound]}#,
#            'verbose': -3}
    
    if max_simulations is not None:
        opts["maxfevals"] = max_simulations
    
    if popsize is not None:
        opts["popsize"] = popsize
    
    if timeout is not None:
        opts["timeout"] = timeout
    
    if tolfun is not None:
        opts["tolfun"] = tolfun
    
    es = cma.CMAEvolutionStrategy(x0, NormScaler.sigma, opts)
    
    return es


def dump_outputs(worker_directory, es, iterator, nh=None):
    
    counter_dict = iterator.get_counter_search_dict()
    
    es_path = os.path.join(worker_directory, 'saved-cma-object.pkl')
    counter_dict_path = os.path.join(worker_directory,
                                      'saved-counter-search-dict.pkl')
    
    pickle.dump(es, open(es_path, 'wb'), -1)
    pickle.dump(counter_dict, open(counter_dict_path, 'wb'), -1)
    
    if nh is None: return
    
    nh_path = os.path.join(worker_directory, 'saved-nh-object.pkl')
    pickle.dump(es, open(nh_path, 'wb'), -1)
    
    return


def load_outputs(worker_directory):
    
    es_path = os.path.join(worker_directory, 'saved-cma-object.pkl')
    nh_path = os.path.join(worker_directory, 'saved-nh-object.pkl')
    counter_dict_path = os.path.join(worker_directory,
                                      'saved-counter-search-dict.pkl')
    
    es = pickle.load(open(es_path, 'rb'))
    counter_dict = pickle.load(open(counter_dict_path, 'rb'))
    
    if os.path.isfile(nh_path):
        nh = None
    else:
        nh = pickle.load(open(nh_path, 'rb'))
    
    return es, counter_dict, nh


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


def _rebuild_input(values, match_dict, input_length):
    
    rebuild = np.zeros(input_length)
    
    for idx, res in values:
        rebuild[idx] = res
    
    for base_idx, copy_idxs in match_dict.iteritems():
        rebuild[copy_idxs] = rebuild[base_idx]
    
    return rebuild
