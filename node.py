'''This module represents the any node/slave in the cluster'''
import os
import psutil
import platform
import itertools

uname = os.uname()

class Node(object):

    platform_name = platform.platform()

    p_num_cores = psutil.cpu_count(logical=False)
    l_num_cores = psutil.cpu_count(logical=True)

    _process_attrs = 'name username pid cpu_percent memory_percent status'.split()

    @staticmethod
    def filter_process(gen, name):
        for p in gen:
            if p.username() == name:
                yield p

    def __init__(self, alias=None):
        self.name = alias or self.platform_name
    
    def _cpu(self):
        '''return those variables that changes'''
        stats = psutil.cpu_stats()

        cpu_info = {
            'cu': psutil.cpu_percent(interval=0.0, percpu=False),
            'cupc': psutil.cpu_percent(interval=0.0, percpu=True),
            "cs": stats.ctx_switches,
            "ci": stats.interrupts,
            "sc": stats.syscalls
        }
        return cpu_info


    def _memory(self):
        mem = psutil.virtual_memory()

        memory_info = {
            't': mem.total // (1024 * 1024),
            'a': mem.available // (1024 * 1024),
            'p': mem.percent
        }
        return memory_info
    
    def _processes(self):
        for process in self.filter_process(psutil.process_iter(), 'user'):
            try:
                pinfo = process.as_dict(attrs=self._process_attrs)
            except psutil.NoSuchProcess:
                pass
            else:
                yield pinfo
    
    def get_info(self):
        return {
            'id': self.name,
            'payload': {
                'cpu': self._cpu(),
                'memory': self._memory(),
                'processes': list(itertools.islice(self._processes(), 20))
            } 
        }








        