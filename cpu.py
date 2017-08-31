import os
import psutil

class CPU(object):
    '''This class gives the metrics of all the CPU usages and so on and so forth'''
    p_num_cores = psutil.cpu_count(logical=False)
    l_num_cores = psutil.cpu_count(logical=True)
    os_name = os.name

    @property
    def cpu_utilization(self):
        return psutil.cpu_percent(interval=0.0, percpu=False)

    @property
    def utilization_per_core(self):
        return psutil.cpu_percent(interval=0.0, percpu=True)

    @property
    def cpu_stats(self):
        return psutil.cpu_stats()

    def get_info(self):
        c_utilization = self.cpu_utilization
        c_utilization_per_core = self.utilization_per_core
        c_stats = self.cpu_stats
        info = {
            "c_utilization": c_utilization,
            "c_utilization_per_core": c_utilization_per_core,
            "ctx_switches": c_stats.ctx_switches,
            "cpu_interrupts": c_stats.interrupts,
            "sys_calls": c_stats.syscalls
        }
        return info