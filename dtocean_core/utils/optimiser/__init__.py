# -*- coding: utf-8 -*-

"""
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import os
import abc
import sys
import time
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


class SafeCMAEvolutionStrategy(cma.CMAEvolutionStrategy):
    
    def plot(self):
        cma.plot(self.logger.name_prefix)
        return


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
    
    def _iterate(self, idx, category, sol, results_queue, *args):
        
        previous_cost = self._counter.get_cost(*args)
        
        if previous_cost:
            results_queue.put((idx, category, sol, previous_cost))
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
        
        results_queue.put((idx, category, sol, cost))
        
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
                       auto_resample_iterations=None,
                       logging="module"):
        
        # Defaults
        if base_penalty is None: base_penalty = 1.
        if num_threads is None: num_threads = 1
        
        self.es = es
        self.nh = nh
        self.iterator = iterator
        self._worker_directory = worker_directory
        self._scaled_vars = scaled_vars
        self._nearest_ops = nearest_ops
        self._fixed_index_map = fixed_index_map
        self._base_penalty = base_penalty
        self._num_threads = num_threads
        self._logging = logging
        self._spare_sols = 1
        self._n_hist = int(10 + 30 * self.es.N / self.es.sp.popsize)
        self._max_resample_loops = None
        self._n_record_resample = None
        self._stop = False
        self._sol_penalty = False
        self._dirty_restart = False
        self._thread_queue = None
        self._sol_feasible = None
        
        self._init_resamples(max_resample_loop_factor,
                             auto_resample_iterations)
        self._init_threads()
        
        return
    
    @property
    def stop(self):
        return self._stop
    
    def _init_resamples(self, max_resample_loop_factor,
                              auto_resample_iterations):
        
        if auto_resample_iterations is None:
            
            if max_resample_loop_factor is None: max_resample_loop_factor = 20
            
            if max_resample_loop_factor < 0:
                err_msg = ("Argument max_resample_loop_factor must be greater "
                           "than or equal to zero")
                raise ValueError(err_msg)
            
            self._n_record_resample = 0
            
            n_default = self.es.popsize
            needed_solutions = (1 + self._spare_sols) * n_default
            self._max_resample_loops = \
                        int(ceil(max_resample_loop_factor * needed_solutions))
            
            log_msg = ("Setting maximum resamples to "
                       "{}").format(self._max_resample_loops)
            module_logger.info(log_msg)
        
        else:
            
            if auto_resample_iterations <= 0:
                err_msg = ("Argument auto_resample_iterations must be greater "
                           "than zero")
                raise ValueError(err_msg)
            
            self._max_resample_loops = 0
            self._n_record_resample = auto_resample_iterations
        
        return
    
    def _init_threads(self):
            
        self._thread_queue = queue.Queue()
        
        for i in range(self._num_threads):
            
            worker = threading.Thread(target=self.iterator,
                                      args=(self._thread_queue,))
            worker.setDaemon(True)
            worker.start()
        
        return
    
    def next(self):
        
        if self.es.stop():
            self._stop = True
            return
        
        if self.nh is None:
            self._next()
        else:
            self._next_nh()
        
        tolfun = max(self.es.fit.fit) - min(self.es.fit.fit)
        tolfunhist = max(self.es.fit.hist) - min(self.es.fit.hist)
        
        if self._logging == "print":
            
            self.es.disp()
            print "    tolfun: {}".format(tolfun)
            print "    tolfunhist: {}".format(tolfunhist)
            
        elif self._logging == "module":
            
            msg_str = ('Minimum fitness for iteration {}: '
                       '{:.15e}').format(self.es.countiter,
                        min(self.es.fit.fit))
            module_logger.info(msg_str)
            
            msg_str = ('Fitness value range (last iteration): '
                       '{}').format(tolfun)
            module_logger.info(msg_str)
            
            msg_str = ('Minimum fitness value range (last {} iterations): '
                       '{}').format(self._n_hist, tolfunhist)
            module_logger.info(msg_str)
        
        return
    
    def _next(self):
        
        default, _ = self._get_solutions_costs(self.es)
        self.es.tell(default["solutions"], default["costs"])
        self.es.logger.add()
        
        return
    
    def _next_nh(self):
        
        # self._sol_penalty is set by self._get_solutions_costs
        if self.es.countiter == 0 or self._sol_penalty or self._dirty_restart:
            scaled_solutions_extra = None
            last_n_evals = None
            self._dirty_restart = False
        else:
            scaled_solutions_extra = self.nh.ask(self.es.ask)
            last_n_evals = self.nh.last_n_evals
        
        default, extra = self._get_solutions_costs(self.es,
                                                   scaled_solutions_extra,
                                                   self.nh.n_evals,
                                                   last_n_evals)
        
        self.es.tell(default["solutions"], default["costs"])
        self.nh.tell(extra["solutions"], extra["costs"])
        
        self.es.sigma *= self.nh.sigma_fac
        self.es.countevals += self.nh.evaluations_just_done
        
        noise = self.nh.get_predicted_noise()
        
        msg = "Last true noise: {}".format(self.nh.noiseS)
        
        if self._logging == "print":
            print msg
        elif self._logging == "module":
            module_logger.info(msg)
        
        msg = "Predicted noise: {}".format(noise)
        
        if self._logging == "print":
            print msg
        elif self._logging == "module":
            module_logger.info(msg)
        
        if abs(noise) <= 1e-12:
            log_noise = 1
        elif noise <= -1e-12:
            log_noise = 0.1
        else:
            log_noise = 10
        
        self.es.logger.add(more_data=[self.nh.evaluations, log_noise])
        self.nh.prepare(default["solutions"], default["costs"])
        
        return
    
    def _get_solutions_costs(self, asktell,
                                   scaled_solutions_extra=None,
                                   n_evals=None,
                                   n_evals_extra=None):
        
        self._sol_penalty = False
        
        final_solutions = []
        final_costs = []
        final_solutions_extra = []
        final_costs_extra = []
        
        result_default = {"solutions": final_solutions,
                          "costs": final_costs}
        result_extra = {"solutions": final_solutions_extra,
                        "costs": final_costs_extra}
        
        n_default = asktell.popsize
        needed_solutions = (1 + self._spare_sols) * n_default
        xmean = None
        
        run_solutions = []
        run_descaled_solutions = []
        resample_loops = -1
        
        while len(run_solutions) < needed_solutions:
            
            # If the maximum number of resamples is reached apply a 
            # penalty value to a new set of solutions
            if (self._n_record_resample == 0 and
                resample_loops == self._max_resample_loops):
                
                log_msg = ("Maximum of {} resamples reached. Only {} of {} "
                           "required solutions were found. Applying "
                           "penalty values.").format(self._max_resample_loops,
                                                     len(run_solutions),
                                                     needed_solutions)
                module_logger.info(log_msg)
                
                run_solutions = []
                run_descaled_solutions = []
                final_solutions.extend(asktell.ask(n_default))
                final_costs.extend(self._get_penalty(final_solutions))
                
                n_default = 0
                
                # Do not assess noise
                self._sol_penalty = True
                
                break
            
            scaled_solutions = asktell.ask(asktell.popsize, xmean)
            
            # Store xmean for resamples
            if xmean is None:
                xmean = asktell.mean.copy()
            
            descaled_solutions = self._get_descaled_solutions(
                                                        scaled_solutions)
            
            checked_solutions = []
            checked_descaled_solutions = []
            
            for sol, des_sol in zip(scaled_solutions, descaled_solutions):
                if self.iterator.pre_constraints_hook(*des_sol): continue
                checked_solutions.append(sol)
                checked_descaled_solutions.append(des_sol)
            
            max_sols = needed_solutions - len(run_solutions)
            checked_solutions = checked_solutions[:max_sols]
            checked_descaled_solutions = checked_descaled_solutions[:max_sols]
            
            run_solutions.extend(checked_solutions)
            run_descaled_solutions.extend(checked_descaled_solutions)
            
            resample_loops += 1
            
            if resample_loops > 0 and checked_solutions:
                
                log_msg = ("{} of {} solutions found after {} resampling "
                           "loops").format(len(run_solutions),
                                           needed_solutions,
                                           resample_loops)
                module_logger.debug(log_msg)
                
                sample_solution = checked_solutions[0]
                sample_solution_strs = [str(x) for x in sample_solution]
                sample_solution_str = ", ".join(sample_solution_strs)
                log_msg = "Sample solution: {}".format(sample_solution_str)
                module_logger.debug(log_msg)
        
        if not self._sol_penalty and resample_loops > 0:
            log_msg = ("{} resamples required to generate {} "
                       "solutions").format(resample_loops, needed_solutions)
            module_logger.info(log_msg)
        
        if self._n_record_resample > 0:
            
            if resample_loops > self._max_resample_loops:
                self._max_resample_loops = resample_loops
            
            self._n_record_resample -= 1
            
            if self._n_record_resample == 0:
                log_msg = ("Setting maximum resamples to {} following "
                           "iteration {}").format(self._max_resample_loops,
                                                  self.es.countiter + 1)
                module_logger.info(log_msg)
        
        categories = ["default"] * len(run_descaled_solutions)
        all_n_evals = [n_evals] * len(run_descaled_solutions)
        
        n_extra = 0
        run_solutions_extra = []
        run_descaled_solutions_extra = []
        categories_extra = []
        all_n_evals_extra = []
        
        if scaled_solutions_extra is not None:
            
            descaled_solutions_extra = self._get_descaled_solutions(
                                                scaled_solutions_extra)
            
            for sol, des_sol in zip(scaled_solutions_extra,
                                    descaled_solutions_extra):
            
                if self.iterator.pre_constraints_hook(*des_sol):
                    final_solutions_extra.append(sol)
                    final_costs_extra.append(np.nan)
                else:
                    run_solutions_extra.append(sol)
                    run_descaled_solutions_extra.append(des_sol)
                    categories_extra.append("extra")
                    n_extra += 1
            
            all_n_evals_extra = [n_evals_extra] * n_extra
        
        if n_extra + n_default == 0:
            return result_default, result_extra
        
        run_solutions = run_solutions_extra + run_solutions
        run_descaled_solutions = run_descaled_solutions_extra + \
                                                    run_descaled_solutions
        categories = categories_extra + categories
        all_n_evals = all_n_evals_extra + all_n_evals
        
        assert (len(run_solutions) ==
                len(run_descaled_solutions) ==
                len(categories) ==
                len(all_n_evals))
        
        run_idxs, match_dict = _get_match_process(run_descaled_solutions,
                                                  categories,
                                                  run_solutions)
        
        result_queue = queue.Queue()
        
        for i in range(n_extra + n_default):
            
            if i not in run_idxs: continue
            category = categories[i]
            sol = run_solutions[i]
            local_n_evals = all_n_evals[i]
            
            self._thread_queue.put([i, category, sol, result_queue] +
                                   run_descaled_solutions[i] + 
                                   [local_n_evals])
        
        store_results = {}
        min_i = 0
        next_i = n_extra + n_default
        results_found = 0
        
        while results_found < n_extra + n_default:
            
            i, category, sol, cost = result_queue.get()
            
            if i in match_dict:
                all_i = [(i, category, sol)] + match_dict[i]
                all_cost = [cost] * (1 + len(match_dict[i]))
            else:
                all_i = [(i, category, sol)]
                all_cost = [cost]
            
            for k, kcost in zip(all_i, all_cost):
                i, category, sol = k
                store_results[i] = (category, sol, kcost)
            
            for check_i in range(min_i, next_i):
                
                if check_i not in store_results: continue
                if check_i == min_i: min_i += 1
                
                result = store_results.pop(check_i)
                
                if result[0] == "extra":
                    
                    final_solutions_extra.append(result[1])
                    final_costs_extra.append(result[2])
                    results_found += 1
                    continue
                
                assert result[0] == "default"
                
                sol = result[1]
                sol_cost = result[2]
                
                if np.isnan(sol_cost):
                    
                    if next_i == len(run_descaled_solutions):
                        
                        log_msg = ("Maximum number of retry solutions "
                                   "reached. Applying penalty value.")
                        module_logger.info(log_msg)
                        
                        sol_cost = self._get_penalty([sol])[0]
                    
                    else:
                        
                        if next_i not in run_idxs:
                            next_i += 1
                            continue
                            
                        run_category = categories[next_i]
                        run_sol = run_solutions[next_i]
                        
                        self._thread_queue.put(
                                [next_i, run_category, run_sol, result_queue] +
                                run_descaled_solutions[next_i] + 
                                [n_evals])
                        
                        next_i += 1
                        continue
                
                final_solutions.append(sol)
                final_costs.append(sol_cost)
                
                results_found += 1
        
        self._thread_queue.join()
        
        return result_default, result_extra
    
    def _get_descaled_solutions(self, scaled_solutions):
        
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
        
        return descaled_solutions
    
    def _get_penalty(self, sols):
        
        if self._sol_feasible is None:
        
            if self.es.countiter == 0:
                err_msg = ("There are no feasible solutions to "
                           "use for penalty calculation. Problem "
                           "is likely ill-posed.")
                raise RuntimeError(err_msg)
            
            self._sol_feasible = self.es.best.x.copy()
        
        costs = [self._base_penalty + norm(
                            sol - self._sol_feasible) for sol in sols]
        
        return costs


def init_evolution_strategy(x0,
                            low_bound,
                            high_bound,
                            max_simulations=None,
                            popsize=None,
                            timeout=None,
                            tolfun=None,
                            logging_directory=None):
    
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
        
    if logging_directory is not None:
        opts['verb_filenameprefix'] = logging_directory + os.sep
    
    es = SafeCMAEvolutionStrategy(x0, NormScaler.sigma, opts)
    
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
    pickle.dump(nh, open(nh_path, 'wb'), -1)
    
    return


def load_outputs(worker_directory):
    
    es_path = os.path.join(worker_directory, 'saved-cma-object.pkl')
    nh_path = os.path.join(worker_directory, 'saved-nh-object.pkl')
    counter_dict_path = os.path.join(worker_directory,
                                      'saved-counter-search-dict.pkl')
    
    es = pickle.load(open(es_path, 'rb'))
    counter_dict = pickle.load(open(counter_dict_path, 'rb'))
    
    if os.path.isfile(nh_path):
        nh = pickle.load(open(nh_path, 'rb'))
    else:
        nh = None
    
    return es, counter_dict, nh


def set_TimedRotatingFileHandler_rollover(timeout=None):
    
    # If theres no timeout choose a big number
    if timeout is None:
        timeout = sys.maxint
    
    logger = logging.Logger.manager.loggerDict["dtocean_core"]
    
    for handler in logger.handlers:
        if handler.__class__.__name__ == "TimedRotatingFileHandler":
            handler.interval = timeout
            handler.rolloverAt = handler.computeRollover(time.time())
    
    return


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


def _get_match_process(values, *args):
    
    def expand_args(x, args):
        
        if not args: return x
        
        result = [x]
        
        for arg in args:
            result.append(arg[x])
        
        return tuple(result)
    
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
        
        if match_list:
            match_list = [expand_args(k, args) for k in match_list]
            match_dict[key] = match_list
    
    process_set = set(range(len(values))) - set(all_matches)
    
    return list(process_set), match_dict
