import psutil


def filter_process(gen, user_name):
    for p in gen:
        if p.username() == user_name:
            yield p

class Process(object):

    def all_user_processes(self):

        _attrs = 'name username pid cpu_percent memory_percent status'.split()
        for process in filter_process(psutil.process_iter(), 'user'):
            try:
                pinfo = process.as_dict(attrs=_attrs)
            except psutil.NoSuchProcess:
                pass
            else:
                
                yield pinfo